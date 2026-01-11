"""
Family & Group Finance Management
=================================
Manage family budgets, split expenses, and household tracking
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import uuid
import sys

sys.path.append(str(Path(__file__).parent.parent))

from database.json_store import JSONStore
from database.user_repository import user_repo
from database.transaction_repository import transaction_repo
from config import DATA_DIR

# Family data store
FAMILIES_DB_FILE = DATA_DIR / "families.json"
families_store = JSONStore(FAMILIES_DB_FILE)


class FamilyFinanceService:
    """Manage family and group finances"""
    
    def __init__(self):
        self.store = families_store
    
    def create_family(self, creator_id: str, name: str, monthly_budget: int = 0) -> Dict:
        """Create a new family/group"""
        
        family_id = str(uuid.uuid4())[:8]
        
        family = {
            "id": family_id,
            "name": name,
            "created_by": creator_id,
            "created_at": datetime.now().isoformat(),
            "members": [
                {
                    "user_id": creator_id,
                    "role": "admin",
                    "joined_at": datetime.now().isoformat()
                }
            ],
            "monthly_budget": monthly_budget,
            "shared_expenses": [],
            "settings": {
                "auto_split": True,
                "notify_all": True,
                "currency": "INR"
            }
        }
        
        self.store.set(family_id, family)
        
        # Update user's family reference
        user_repo.update_user(creator_id, {"family_id": family_id, "family_role": "admin"})
        
        return family
    
    def join_family(self, family_id: str, user_id: str) -> Dict:
        """Join an existing family"""
        
        family = self.store.get(family_id)
        if not family:
            return {"success": False, "error": "Family not found"}
        
        # Check if already a member
        for member in family["members"]:
            if member["user_id"] == user_id:
                return {"success": False, "error": "Already a member"}
        
        # Add member
        family["members"].append({
            "user_id": user_id,
            "role": "member",
            "joined_at": datetime.now().isoformat()
        })
        
        self.store.set(family_id, family)
        
        # Update user
        user_repo.update_user(user_id, {"family_id": family_id, "family_role": "member"})
        
        return {"success": True, "family": family}
    
    def add_shared_expense(
        self,
        family_id: str,
        amount: int,
        category: str,
        description: str,
        paid_by: str,
        split_type: str = "equal",  # equal, percentage, custom
        split_details: Dict = None
    ) -> Dict:
        """Add a shared expense to the family"""
        
        family = self.store.get(family_id)
        if not family:
            return {"success": False, "error": "Family not found"}
        
        members = family["members"]
        num_members = len(members)
        
        # Calculate splits
        if split_type == "equal":
            per_person = amount / num_members
            splits = {m["user_id"]: per_person for m in members}
        elif split_type == "percentage" and split_details:
            splits = {uid: amount * pct / 100 for uid, pct in split_details.items()}
        elif split_type == "custom" and split_details:
            splits = split_details
        else:
            per_person = amount / num_members
            splits = {m["user_id"]: per_person for m in members}
        
        expense = {
            "id": str(uuid.uuid4())[:8],
            "amount": amount,
            "category": category,
            "description": description,
            "paid_by": paid_by,
            "split_type": split_type,
            "splits": splits,
            "date": datetime.now().isoformat(),
            "settled": False,
            "settlements": []
        }
        
        family["shared_expenses"].append(expense)
        self.store.set(family_id, family)
        
        return {"success": True, "expense": expense}
    
    def get_family_summary(self, family_id: str) -> Dict:
        """Get family expense summary"""
        
        family = self.store.get(family_id)
        if not family:
            return {"error": "Family not found"}
        
        total_shared = 0
        by_category = {}
        by_member = {m["user_id"]: {"paid": 0, "owes": 0} for m in family["members"]}
        
        for expense in family["shared_expenses"]:
            total_shared += expense["amount"]
            
            # Category breakdown
            cat = expense["category"]
            if cat not in by_category:
                by_category[cat] = 0
            by_category[cat] += expense["amount"]
            
            # Member breakdown
            paid_by = expense["paid_by"]
            if paid_by in by_member:
                by_member[paid_by]["paid"] += expense["amount"]
            
            for user_id, share in expense["splits"].items():
                if user_id in by_member:
                    by_member[user_id]["owes"] += share
        
        # Calculate balances
        for user_id in by_member:
            by_member[user_id]["balance"] = by_member[user_id]["paid"] - by_member[user_id]["owes"]
        
        return {
            "family_name": family["name"],
            "member_count": len(family["members"]),
            "monthly_budget": family.get("monthly_budget", 0),
            "total_shared_expenses": total_shared,
            "by_category": by_category,
            "by_member": by_member,
            "expense_count": len(family["shared_expenses"])
        }
    
    def get_settlements_needed(self, family_id: str) -> List[Dict]:
        """Calculate settlements needed between members"""
        
        summary = self.get_family_summary(family_id)
        if "error" in summary:
            return []
        
        by_member = summary["by_member"]
        
        # Separate debtors and creditors
        debtors = []
        creditors = []
        
        for user_id, data in by_member.items():
            balance = data["balance"]
            if balance < -1:  # Owes money
                debtors.append({"user_id": user_id, "amount": abs(balance)})
            elif balance > 1:  # Owed money
                creditors.append({"user_id": user_id, "amount": balance})
        
        # Sort
        debtors.sort(key=lambda x: x["amount"], reverse=True)
        creditors.sort(key=lambda x: x["amount"], reverse=True)
        
        # Generate settlements
        settlements = []
        
        i, j = 0, 0
        while i < len(debtors) and j < len(creditors):
            debtor = debtors[i]
            creditor = creditors[j]
            
            settle_amount = min(debtor["amount"], creditor["amount"])
            
            settlements.append({
                "from": debtor["user_id"],
                "to": creditor["user_id"],
                "amount": round(settle_amount, 2)
            })
            
            debtor["amount"] -= settle_amount
            creditor["amount"] -= settle_amount
            
            if debtor["amount"] < 1:
                i += 1
            if creditor["amount"] < 1:
                j += 1
        
        return settlements
    
    def set_family_budget(self, family_id: str, monthly_budget: int, categories: Dict = None) -> Dict:
        """Set monthly budget for family"""
        
        family = self.store.get(family_id)
        if not family:
            return {"success": False, "error": "Family not found"}
        
        family["monthly_budget"] = monthly_budget
        
        if categories:
            family["budget_categories"] = categories
        else:
            # Default allocation
            family["budget_categories"] = {
                "food": int(monthly_budget * 0.30),
                "rent": int(monthly_budget * 0.25),
                "utilities": int(monthly_budget * 0.10),
                "transport": int(monthly_budget * 0.10),
                "healthcare": int(monthly_budget * 0.05),
                "education": int(monthly_budget * 0.05),
                "entertainment": int(monthly_budget * 0.05),
                "savings": int(monthly_budget * 0.10),
            }
        
        self.store.set(family_id, family)
        
        return {"success": True, "budget": family["budget_categories"]}
    
    def get_family_budget_status(self, family_id: str) -> Dict:
        """Get current budget status for family"""
        
        family = self.store.get(family_id)
        if not family:
            return {"error": "Family not found"}
        
        budget = family.get("monthly_budget", 0)
        categories = family.get("budget_categories", {})
        
        # Calculate current month spending
        current_month = datetime.now().strftime("%Y-%m")
        spent_by_category = {}
        total_spent = 0
        
        for expense in family.get("shared_expenses", []):
            exp_date = expense.get("date", "")
            if exp_date.startswith(current_month):
                cat = expense["category"]
                if cat not in spent_by_category:
                    spent_by_category[cat] = 0
                spent_by_category[cat] += expense["amount"]
                total_spent += expense["amount"]
        
        # Compare with budget
        status = {}
        for cat, limit in categories.items():
            spent = spent_by_category.get(cat, 0)
            remaining = limit - spent
            percent = int(spent / max(limit, 1) * 100)
            
            if percent >= 100:
                health = "🔴"
            elif percent >= 80:
                health = "🟡"
            else:
                health = "🟢"
            
            status[cat] = {
                "budget": limit,
                "spent": spent,
                "remaining": remaining,
                "percent": percent,
                "health": health
            }
        
        return {
            "total_budget": budget,
            "total_spent": total_spent,
            "total_remaining": budget - total_spent,
            "percent_used": int(total_spent / max(budget, 1) * 100),
            "by_category": status
        }
    
    def get_member_contribution(self, family_id: str) -> List[Dict]:
        """Get each member's contribution to family expenses"""
        
        summary = self.get_family_summary(family_id)
        if "error" in summary:
            return []
        
        contributions = []
        total = summary["total_shared_expenses"]
        
        for user_id, data in summary["by_member"].items():
            user = user_repo.get_user(user_id)
            name = user.get("name", "Member") if user else "Unknown"
            
            percent = int(data["paid"] / max(total, 1) * 100)
            
            contributions.append({
                "user_id": user_id,
                "name": name,
                "paid": data["paid"],
                "owes": data["owes"],
                "balance": data["balance"],
                "contribution_percent": percent
            })
        
        contributions.sort(key=lambda x: x["paid"], reverse=True)
        
        return contributions
    
    def generate_family_report_text(self, family_id: str) -> str:
        """Generate text report for family"""
        
        family = self.store.get(family_id)
        if not family:
            return "Family not found"
        
        summary = self.get_family_summary(family_id)
        budget_status = self.get_family_budget_status(family_id)
        settlements = self.get_settlements_needed(family_id)
        contributions = self.get_member_contribution(family_id)
        
        report = f"""
👨‍👩‍👧‍👦 *{family['name']} - Family Finance Report*
━━━━━━━━━━━━━━━━━━━━━━

👥 *Members:* {summary['member_count']}
💰 *Monthly Budget:* ₹{summary['monthly_budget']:,}
💸 *Total Shared Expenses:* ₹{summary['total_shared_expenses']:,}

📊 *Budget Status:*
"""
        
        for cat, status in budget_status.get("by_category", {}).items():
            report += f"\n{status['health']} {cat.title()}: ₹{status['spent']:,} / ₹{status['budget']:,} ({status['percent']}%)"
        
        report += "\n\n👥 *Member Contributions:*"
        for member in contributions:
            balance_emoji = "✅" if member["balance"] >= 0 else "⚠️"
            report += f"\n{balance_emoji} {member['name']}: Paid ₹{int(member['paid']):,} | Balance: ₹{int(member['balance']):,}"
        
        if settlements:
            report += "\n\n💸 *Settlements Needed:*"
            for s in settlements:
                from_user = user_repo.get_user(s["from"])
                to_user = user_repo.get_user(s["to"])
                from_name = from_user.get("name", "?") if from_user else "?"
                to_name = to_user.get("name", "?") if to_user else "?"
                report += f"\n• {from_name} → {to_name}: ₹{int(s['amount']):,}"
        
        report += "\n\n━━━━━━━━━━━━━━━━━━━━━━"
        
        return report


# Global instance
family_service = FamilyFinanceService()

