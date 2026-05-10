# Orthogonal Verifier Core

Orthogonal Verifier Core is an experimental verifier-first framework for detecting false closure in AI, automation, crypto, and complex decision systems.

False closure occurs when a system appears to have reached a valid answer or action, but has not actually satisfied the original success condition.

## Core Idea

Proposal engines can be creative. Verifiers must be strict.

The verifier evaluates whether a proposed action, claim, route, or output actually returns to the original success condition.

## Core Pipeline

1. Define the original success condition.
2. Identify the native burden.
3. Evaluate the proposed bridge, claim, or action.
4. Test whether the result returns to the original condition.
5. Accept, block, or return a structured failure certificate.

## Output Types

- `PASS` — the proposed action satisfies all required return conditions.
- `BLOCK` — the proposed action fails critical return conditions.
- `REVIEW` — the proposed action has unresolved uncertainty and needs human review.

## Example Use Cases

- AI output verification
- Crypto route validation
- Autonomous-agent safety checks
- Technical claim auditing
- Compliance decision support
- Bot execution firewalls
- Research and whitepaper review

## Example: Crypto Route Verification

A trading bot proposes a route with nominal profit.

The verifier checks:

- quote freshness
- fee-adjusted return
- slippage-adjusted return
- liquidity confidence
- wallet-level profit

If the proposed route does not satisfy these return conditions, the verifier blocks execution and returns a failure certificate.

## Example Output

```text
VerificationResult(
    decision='BLOCK',
    closure_score=0.0,
    passed_conditions=[],
    failed_conditions=[
        'positive_net_profit',
        'minimum_profit_buffer',
        'fresh_quote',
        'liquidity_confidence'
    ],
    review_conditions=[],
    failure_certificate=[
        'positive_net_profit: Net profit after fees/slippage is -0.0800%.',
        'minimum_profit_buffer: Net profit -0.0800% does not meet required buffer.',
        'fresh_quote: Quote age is 6.40 seconds.',
        'liquidity_confidence: Liquidity score is 0.52.'
    ],
    metadata={
        'nominal_profit_pct': 0.42,
        'net_profit_pct': -0.08,
        'quote_age_seconds': 6.4,
        'liquidity_score': 0.52
    }
)
