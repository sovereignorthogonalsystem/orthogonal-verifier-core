from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ReturnCondition:
    """
    A single required condition that a proposed action, claim, or output
    must satisfy before it can be considered verified.

    Example:
        name="fresh_quote"
        passed=True
        detail="Quote age is 1.2 seconds."
        weight=1.5
    """

    name: str
    passed: bool
    detail: str
    weight: float = 1.0


@dataclass
class VerificationResult:
    """
    Structured result returned by the verifier.

    decision:
        PASS, BLOCK, or REVIEW

    closure_score:
        Weighted fraction of satisfied return conditions.

    failure_certificate:
        Human-readable explanation of why the proposed closure failed.
    """

    decision: str
    closure_score: float
    passed_conditions: List[str] = field(default_factory=list)
    failed_conditions: List[str] = field(default_factory=list)
    review_conditions: List[str] = field(default_factory=list)
    failure_certificate: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class OrthogonalVerifier:
    """
    A lightweight verifier for detecting false closure.

    The verifier does not generate a proposal.
    It evaluates whether the proposal satisfies its required return conditions.

    Core principle:
        Proposal engines can be creative. Verifiers must be strict.
    """

    def __init__(self, pass_threshold: float = 0.85, review_threshold: float = 0.60):
        if not 0 <= review_threshold <= pass_threshold <= 1:
            raise ValueError(
                "Thresholds must satisfy 0 <= review_threshold <= pass_threshold <= 1."
            )

        self.pass_threshold = pass_threshold
        self.review_threshold = review_threshold

    def evaluate(
        self,
        conditions: List[ReturnCondition],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> VerificationResult:
        """
        Evaluate a list of return conditions.

        Returns:
            VerificationResult with PASS, BLOCK, or REVIEW.
        """

        metadata = metadata or {}

        if not conditions:
            return VerificationResult(
                decision="REVIEW",
                closure_score=0.0,
                review_conditions=["No return conditions supplied."],
                failure_certificate=[
                    "Cannot verify closure without explicit return conditions."
                ],
                metadata=metadata,
            )

        total_weight = sum(max(condition.weight, 0.0) for condition in conditions)

        if total_weight == 0:
            return VerificationResult(
                decision="REVIEW",
                closure_score=0.0,
                review_conditions=["All return-condition weights are zero."],
                failure_certificate=[
                    "Cannot compute meaningful closure score from zero-weight conditions."
                ],
                metadata=metadata,
            )

        passed_weight = sum(
            condition.weight
            for condition in conditions
            if condition.passed and condition.weight > 0
        )

        closure_score = passed_weight / total_weight

        passed_conditions = [
            condition.name for condition in conditions if condition.passed
        ]

        failed_conditions = [
            condition.name for condition in conditions if not condition.passed
        ]

        failure_certificate = [
            f"{condition.name}: {condition.detail}"
            for condition in conditions
            if not condition.passed
        ]

        if closure_score >= self.pass_threshold and not failed_conditions:
            decision = "PASS"
        elif closure_score >= self.review_threshold:
            decision = "REVIEW"
        else:
            decision = "BLOCK"

        return VerificationResult(
            decision=decision,
            closure_score=round(closure_score, 4),
            passed_conditions=passed_conditions,
            failed_conditions=failed_conditions,
            review_conditions=failed_conditions if decision == "REVIEW" else [],
            failure_certificate=failure_certificate,
            metadata=metadata,
        )


def verify_crypto_route(route: Dict[str, Any]) -> VerificationResult:
    """
    Example verifier for a proposed crypto route.

    This is not financial advice.

    It demonstrates the false-closure pattern:
    nominal profit is not accepted unless it returns to wallet-level profit
    after fees, slippage, quote freshness, and liquidity checks.
    """

    nominal_profit_pct = float(route.get("nominal_profit_pct", 0.0))
    estimated_fees_pct = float(route.get("estimated_fees_pct", 0.0))
    estimated_slippage_pct = float(route.get("estimated_slippage_pct", 0.0))
    quote_age_seconds = float(route.get("quote_age_seconds", 999.0))
    liquidity_score = float(route.get("liquidity_score", 0.0))

    minimum_profit_pct = float(route.get("minimum_profit_pct", 0.25))
    max_quote_age_seconds = float(route.get("max_quote_age_seconds", 3.0))
    minimum_liquidity_score = float(route.get("minimum_liquidity_score", 0.70))

    net_profit_pct = nominal_profit_pct - estimated_fees_pct - estimated_slippage_pct

    conditions = [
        ReturnCondition(
            name="positive_net_profit",
            passed=net_profit_pct > 0,
            detail=f"Net profit after fees/slippage is {net_profit_pct:.4f}%.",
            weight=3.0,
        ),
        ReturnCondition(
            name="minimum_profit_buffer",
            passed=net_profit_pct >= minimum_profit_pct,
            detail=(
                f"Net profit {net_profit_pct:.4f}% does not meet "
                f"required buffer of {minimum_profit_pct:.4f}%."
            ),
            weight=2.0,
        ),
        ReturnCondition(
            name="fresh_quote",
            passed=quote_age_seconds <= max_quote_age_seconds,
            detail=(
                f"Quote age is {quote_age_seconds:.2f} seconds; "
                f"maximum allowed is {max_quote_age_seconds:.2f}."
            ),
            weight=1.5,
        ),
        ReturnCondition(
            name="liquidity_confidence",
            passed=liquidity_score >= minimum_liquidity_score,
            detail=(
                f"Liquidity score is {liquidity_score:.2f}; "
                f"minimum required is {minimum_liquidity_score:.2f}."
            ),
            weight=1.5,
        ),
    ]

    verifier = OrthogonalVerifier()

    return verifier.evaluate(
        conditions,
        metadata={
            "nominal_profit_pct": nominal_profit_pct,
            "estimated_fees_pct": estimated_fees_pct,
            "estimated_slippage_pct": estimated_slippage_pct,
            "net_profit_pct": round(net_profit_pct, 4),
            "quote_age_seconds": quote_age_seconds,
            "liquidity_score": liquidity_score,
        },
    )


def verify_ai_claim(payload: Dict[str, Any]) -> VerificationResult:
    """
    Example verifier for an AI-generated claim.

    It checks whether the answer satisfies basic return conditions:
    relevance, evidence, uncertainty handling, and no unsupported high-risk claim.
    """

    conditions = [
        ReturnCondition(
            name="answers_original_request",
            passed=bool(payload.get("answers_original_request", False)),
            detail="The answer does not clearly satisfy the original user request.",
            weight=2.0,
        ),
        ReturnCondition(
            name="evidence_attached",
            passed=bool(payload.get("evidence_attached", False)),
            detail="The answer makes claims without attached evidence.",
            weight=2.0,
        ),
        ReturnCondition(
            name="uncertainty_flagged",
            passed=bool(payload.get("uncertainty_flagged", False)),
            detail="The answer does not flag uncertainty or missing information.",
            weight=1.0,
        ),
        ReturnCondition(
            name="no_unsupported_high_risk_claim",
            passed=bool(payload.get("no_unsupported_high_risk_claim", False)),
            detail="The answer contains at least one unsupported high-risk claim.",
            weight=3.0,
        ),
    ]

    verifier = OrthogonalVerifier()

    return verifier.evaluate(
        conditions,
        metadata={
            "user_request": payload.get("user_request"),
            "ai_answer": payload.get("ai_answer"),
        },
    )


if __name__ == "__main__":
    example_route = {
        "nominal_profit_pct": 0.42,
        "estimated_fees_pct": 0.12,
        "estimated_slippage_pct": 0.38,
        "quote_age_seconds": 6.4,
        "liquidity_score": 0.52,
        "minimum_profit_pct": 0.25,
        "max_quote_age_seconds": 3,
        "minimum_liquidity_score": 0.70,
    }

    result = verify_crypto_route(example_route)
    print(result)
