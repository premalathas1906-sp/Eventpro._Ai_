# app/ai/budget_engine.py
"""
Budget Recommendation Engine for EventPro AI.

Provides intelligent budget allocation, per-person cost estimates,
venue suggestions, and actionable money-saving tips based on
event type, guest count, and total budget.
"""

from __future__ import annotations


class BudgetEngine:
    """
    Generates smart budget breakdowns and recommendations.

    Usage::

        engine = BudgetEngine()
        result = engine.get_recommendations(
            total_budget=500_000,
            event_type='Wedding',
            guest_count=200,
        )
    """

    # ── Base allocation ratios per event type ───────────────────────────
    ALLOCATION_RATIOS: dict[str, dict[str, float]] = {
        "Wedding": {
            "Venue": 0.30,
            "Catering": 0.35,
            "Decorations": 0.15,
            "Photography": 0.10,
            "Entertainment": 0.05,
            "Miscellaneous": 0.05,
        },
        "Birthday": {
            "Venue": 0.20,
            "Catering": 0.30,
            "Decorations": 0.20,
            "Entertainment": 0.20,
            "Photography": 0.05,
            "Miscellaneous": 0.05,
        },
        "College Event": {
            "Venue": 0.25,
            "Catering": 0.25,
            "Decorations": 0.15,
            "Tech/AV": 0.15,
            "Marketing": 0.10,
            "Miscellaneous": 0.10,
        },
        "Corporate": {
            "Venue": 0.35,
            "Catering": 0.30,
            "Tech/AV": 0.15,
            "Decorations": 0.10,
            "Entertainment": 0.05,
            "Miscellaneous": 0.05,
        },
    }

    # ── Cost-saving tips per event type ─────────────────────────────────
    _TIPS: dict[str, list[str]] = {
        "Wedding": [
            "Book your venue and caterer together – many offer 10-15% combo discounts.",
            "Choose in-season flowers to cut decoration costs by up to 30%.",
            "Consider a weekday or off-season date for venue savings of 20-40%.",
            "Hire a student photographer for candid shots alongside the main photographer.",
            "Use digital invitations to save ₹5,000-15,000 on printing & postage.",
            "Opt for a buffet instead of a plated dinner to reduce per-plate cost.",
        ],
        "Birthday": [
            "Host at home or a public park to eliminate venue rental fees.",
            "DIY decorations with balloon arches and streamers – just as festive!",
            "Order a statement cake and supplement with cupcakes for large groups.",
            "Create a collaborative Spotify playlist instead of hiring a DJ.",
            "Use digital invites via WhatsApp or email to save on printing.",
        ],
        "College Event": [
            "Use campus venues – most are free or heavily subsidised for student events.",
            "Seek sponsorships from local businesses to offset 30-50% of costs.",
            "Use student volunteers for setup, registration, and AV management.",
            "Go with pizza/wraps instead of plated meals – cheaper and crowd-pleasing.",
            "Promote via social media and campus boards to eliminate marketing spend.",
            "Borrow AV equipment from the college media lab.",
        ],
        "Corporate": [
            "Book conference hotels with bundled AV and catering packages.",
            "Use digital signage and projections instead of printed banners.",
            "Negotiate early-bird pricing – book 3+ months in advance.",
            "Choose a continental breakfast buffet over a full sit-down meal.",
            "Record sessions in-house instead of hiring a professional videographer.",
            "Leverage employee speakers instead of paid keynotes for internal events.",
        ],
    }

    # ── Venue tiers ─────────────────────────────────────────────────────
    _VENUE_TIERS: list[dict] = [
        {
            "tier": "Budget-Friendly",
            "max_per_person": 500,
            "options": [
                "Community hall",
                "Rooftop terrace",
                "Public garden / park",
                "College auditorium",
                "Co-working event space",
            ],
        },
        {
            "tier": "Mid-Range",
            "max_per_person": 1500,
            "options": [
                "Banquet hall",
                "Restaurant private dining",
                "Hotel conference room",
                "Boutique farmhouse",
                "Art gallery / loft space",
            ],
        },
        {
            "tier": "Premium",
            "max_per_person": 3000,
            "options": [
                "5-star hotel ballroom",
                "Luxury resort",
                "Heritage palace / haveli",
                "Waterfront venue",
                "Private island / estate",
            ],
        },
    ]

    # ── Public API ──────────────────────────────────────────────────────
    def get_recommendations(
        self,
        total_budget: float,
        event_type: str,
        guest_count: int,
    ) -> dict:
        """
        Generate a full budget recommendation.

        Parameters
        ----------
        total_budget : float
            Total available budget in ₹.
        event_type : str
            One of 'Wedding', 'Birthday', 'College Event', 'Corporate'.
        guest_count : int
            Expected number of guests.

        Returns
        -------
        dict
            Keys: allocations, recommendations, per_person_cost,
                  venues, budget_health, savings_potential.
        """
        if total_budget <= 0 or guest_count <= 0:
            return {
                "allocations": [],
                "recommendations": ["Please provide a valid budget and guest count."],
                "per_person_cost": 0,
                "venues": [],
                "budget_health": "Unknown",
                "savings_potential": 0,
            }

        # 1. Resolve ratios (fallback to Corporate if type is unknown)
        ratios = dict(
            self.ALLOCATION_RATIOS.get(event_type, self.ALLOCATION_RATIOS["Corporate"])
        )

        # 2. Adjust for large guest counts – catering scales up
        ratios = self._adjust_for_guest_count(ratios, guest_count)

        # 3. Calculate allocations
        allocations = []
        for category, pct in ratios.items():
            amount = round(total_budget * pct, 2)
            allocations.append(
                {
                    "category": category,
                    "amount": amount,
                    "percentage": round(pct * 100, 1),
                    "per_person": round(amount / guest_count, 2),
                }
            )

        # 4. Per-person cost
        per_person = round(total_budget / guest_count, 2)

        # 5. Budget-health indicator
        budget_health = self._assess_budget_health(per_person, event_type)

        # 6. Specific tips
        tips = self._TIPS.get(event_type, self._TIPS["Corporate"])
        recommendations = list(tips)  # copy

        # Extra contextual recommendations
        if per_person < 300:
            recommendations.insert(
                0,
                "⚠️ Your per-person budget is very tight. "
                "Consider reducing the guest list or increasing the budget.",
            )
        elif per_person > 5000:
            recommendations.insert(
                0,
                "💡 You have a generous per-person budget. "
                "Consider upgrading to premium vendors and luxury décor.",
            )

        if guest_count > 300:
            recommendations.append(
                "For 300+ guests, negotiate bulk catering rates – "
                "most caterers offer 10-20% discounts at this scale."
            )

        # 7. Venue suggestions
        venues = self.get_venue_suggestions(total_budget, guest_count)

        # 8. Savings potential estimate (5-15% of budget)
        savings_potential = round(total_budget * 0.10, 2)

        return {
            "allocations": allocations,
            "recommendations": recommendations,
            "per_person_cost": per_person,
            "venues": venues,
            "budget_health": budget_health,
            "savings_potential": savings_potential,
        }

    def get_venue_suggestions(
        self,
        budget: float,
        guest_count: int,
    ) -> list[dict]:
        """
        Return venue suggestions based on per-person budget.

        Each suggestion dict has keys: tier, venues (list[str]), fit (str).
        """
        per_person = budget / guest_count if guest_count else 0
        suggestions: list[dict] = []

        for tier_info in self._VENUE_TIERS:
            if per_person <= tier_info["max_per_person"] * 1.5:
                fit = "✅ Great fit" if per_person <= tier_info["max_per_person"] else "⚠️ Stretch"
                suggestions.append(
                    {
                        "tier": tier_info["tier"],
                        "venues": tier_info["options"],
                        "fit": fit,
                        "estimated_venue_cost": f"₹{int(tier_info['max_per_person'] * 0.3 * guest_count):,}",
                    }
                )

        # Always include at least the budget-friendly tier
        if not suggestions:
            suggestions.append(
                {
                    "tier": self._VENUE_TIERS[0]["tier"],
                    "venues": self._VENUE_TIERS[0]["options"],
                    "fit": "✅ Great fit",
                    "estimated_venue_cost": f"₹{int(self._VENUE_TIERS[0]['max_per_person'] * 0.3 * guest_count):,}",
                }
            )

        return suggestions

    # ── Internal helpers ────────────────────────────────────────────────
    @staticmethod
    def _adjust_for_guest_count(
        ratios: dict[str, float],
        guest_count: int,
    ) -> dict[str, float]:
        """
        Shift allocation toward catering for large events.

        For 200+ guests, catering share grows by up to 8 pp; the increase
        is taken proportionally from non-catering categories.
        """
        if guest_count < 200 or "Catering" not in ratios:
            return ratios

        # Scale factor: +0.02 per 100 guests above 200, max +0.08
        extra = min(0.08, (guest_count - 200) / 100 * 0.02)
        others = [k for k in ratios if k != "Catering"]
        deduction_each = extra / len(others) if others else 0

        adjusted = {}
        for k, v in ratios.items():
            if k == "Catering":
                adjusted[k] = v + extra
            else:
                adjusted[k] = max(0.02, v - deduction_each)  # floor at 2%

        # Re-normalise to 1.0
        total = sum(adjusted.values())
        return {k: round(v / total, 4) for k, v in adjusted.items()}

    @staticmethod
    def _assess_budget_health(per_person: float, event_type: str) -> str:
        """
        Return a qualitative label for the budget adequacy.

        Thresholds are event-type-aware.
        """
        thresholds = {
            "Wedding":       {"low": 500,  "good": 1500, "great": 3000},
            "Birthday":      {"low": 200,  "good": 800,  "great": 2000},
            "College Event": {"low": 150,  "good": 500,  "great": 1000},
            "Corporate":     {"low": 400,  "good": 1200, "great": 2500},
        }
        t = thresholds.get(event_type, thresholds["Corporate"])

        if per_person < t["low"]:
            return "🔴 Tight – consider reducing scope or increasing budget"
        if per_person < t["good"]:
            return "🟡 Moderate – careful planning recommended"
        if per_person < t["great"]:
            return "🟢 Healthy – good balance of quality and value"
        return "💎 Premium – room for luxury options"
