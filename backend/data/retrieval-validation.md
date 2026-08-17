# Retrieval@3 Validation Queries

Use these queries after indexing every file in `sample-docs/`. For each query,
record whether one of the top three retrieved chunks contains the expected fact.

| # | Query | Expected source | Expected fact |
|---|---|---|---|
| 1 | How many annual-leave days do full-time employees receive? | `employee-handbook.txt` | 21 paid days per calendar year |
| 2 | How far in advance should I request annual leave? | `employee-handbook.txt` | At least five working days |
| 3 | How many remote-working days are allowed each week? | `employee-handbook.txt` | Up to two days with manager approval |
| 4 | When is a medical note required for sick leave? | `employee-handbook.txt` | Three or more consecutive working days |
| 5 | Is multi-factor authentication required for the company VPN? | `it-security-policy.txt` | Yes, MFA is required |
| 6 | When must a lost company device be reported? | `it-security-policy.txt` | Within one hour of discovery |
| 7 | Can I send customer records to my personal email? | `it-security-policy.txt` | No, confidential data must stay in approved systems |
| 8 | What counts as a severity-one support incident? | `customer-support-guide.txt` | Complete production outage or confirmed data loss affecting multiple customers |
| 9 | How quickly must severity-one incidents be acknowledged? | `customer-support-guide.txt` | Within one hour |
| 10 | What details belong in an escalated incident ticket? | `customer-support-guide.txt` | Customer, service, start time, impact, and attempted steps |
| 11 | What should I complete in my first week? | `new-hire-onboarding.txt` | Security training, MFA setup, and manager meeting for 30-day goals |
| 12 | What is the annual learning budget? | `new-hire-onboarding.txt` | 30,000 KES |
| 13 | How long is the standard probation period? | `new-hire-onboarding.txt` | Six months |
| 14 | When must expense claims be submitted? | `expense-faq.txt` | Within 30 days of purchase |
| 15 | What is the domestic business-travel meal allowance? | `expense-faq.txt` | Up to 2,500 KES per day |

## Recording Results

Run all 15 queries and mark each query as a pass when its expected source appears
in the API response's `sources` list. Calculate Retrieval@3 as:

```text
passed queries / 15 * 100
```

The project target is at least 80%.
