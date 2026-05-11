# False Closure

False closure occurs when a system appears to have reached a valid conclusion, but the conclusion does not actually satisfy the original success condition.

## Core Rule

No proposed output is accepted until it returns to the original success condition.

## Examples

### Crypto

A route appears profitable before fees and slippage.

False closure:

- nominal profit is positive
- route appears executable
- quote appears favorable

Required return:

- wallet-level profit remains positive after fees
- wallet-level profit remains positive after slippage
- quote is fresh
- liquidity is sufficient
- route can actually execute

### AI

An AI answer sounds coherent.

False closure:

- answer is fluent
- answer is confident
- answer resembles expert language

Required return:

- answer satisfies the original request
- answer is supported by evidence
- uncertainty is flagged
- high-risk claims are not made without support

## Failure Certificate

When closure fails, the verifier should return a structured explanation.
