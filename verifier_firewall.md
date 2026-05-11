# Verifier Firewall

A verifier firewall separates proposal from acceptance.

A proposal engine may generate candidate actions, claims, routes, or explanations.

The verifier firewall decides whether those candidates are allowed to pass.

## Principle

Proposal engines can be creative. Verifiers must be strict.

## Basic Flow

1. Proposal is generated.
2. Required return conditions are defined.
3. Verifier evaluates each return condition.
4. System returns `PASS`, `BLOCK`, or `REVIEW`.
5. If blocked, the verifier produces a failure certificate.

## Output Types

### PASS

The proposed output satisfies the required return conditions.

### BLOCK

The proposed output fails critical return conditions.

### REVIEW

The proposed output has partial support but unresolved uncertainty remains.

## Failure Certificate

A failure certificate explains why closure was not accepted.

Example:

BLOCK — false closure detected.

The proposed crypto route has positive nominal profit, but net profit after estimated fees and slippage is negative.
The quote is stale.
Liquidity confidence is below threshold.
