# Trigger Evaluation Methodology

## 1. How skill triggering works

In a typical skill platform, triggering starts from the skill description. The platform compares an incoming user request against that description and related trigger wording, then decides whether to activate the skill.

For this evaluator, we use a simple proxy:

1. read the skill description
2. extract keywords from that description
3. compare a test query against those keywords
4. mark the skill as triggered when keyword overlap crosses a threshold

Real platforms often use semantic matching or embeddings. This evaluator does not. It uses keyword overlap because it is transparent, reproducible, and good enough for quick trigger QA.

## 2. Test set design

Each skill should be tested with both positive and negative examples.

- **Positive set**: 8-10 realistic queries that should activate the skill
- **Negative set**: 8-10 realistic queries that should not activate the skill

This size is large enough to expose obvious gaps without becoming expensive to maintain.

## 3. Metrics

### trigger_pass_rate

Percentage of positive queries that correctly match.

Formula:

`passed_positive / total_positive`

### false_positive_rate

Percentage of negative queries that incorrectly match.

Formula:

`failed_negative / total_negative`

### false_negative_rate

Percentage of positive queries that fail to match.

Formula:

`failed_positive / total_positive`

## 4. Thresholds

Recommended minimums:

- `trigger_pass_rate >= 0.80`
- `false_positive_rate <= 0.15`

If pass rate is below the threshold, the description is usually too vague, too narrow, or missing key phrases.

If false positive rate is above the threshold, the description is usually too broad or shares too much vocabulary with unrelated workflows.

## 5. How to write good test queries

Good trigger tests should be:

- **specific**: reflect a real user request, not abstract keywords
- **realistic**: phrased the way users actually ask for help
- **diverse**: vary wording so the evaluator checks more than one sentence pattern
- **boundary-aware**: include near-miss prompts that are related but should still stay negative

Recommended query mix:

- direct requests
- short natural-language prompts
- longer prompts with context
- paraphrases of the same intention
- boundary cases that mention adjacent domains

Bad examples:

- `trigger test`
- `deploy`
- `skill help`

These are too short and too ambiguous to tell you much.

## 6. Example test set: deploy-helper

Hypothetical skill: `deploy-helper`

### Positive queries

1. Deploy this repo to a staging server.
2. Help me roll out this service to production.
3. I need a deployment plan for this application.
4. Verify whether my deploy process is safe.
5. Set up a release workflow for this backend.
6. Run a smoke check after deployment.
7. How should I deploy this app with rollback points?
8. Validate the server is ready before deploying.
9. Help me put this API online.

### Negative queries

1. Rewrite this README in clearer English.
2. Generate unit tests for a Python module.
3. Explain how this SQL query works.
4. Create a skill for linting Markdown files.
5. Summarize this architecture diagram.
6. Review the security of this shell script.
7. Draft interview questions for a backend engineer.
8. Convert these notes into a slide outline.
9. Help me debug a TypeScript type error.

## 7. Interpreting results

- High pass rate + low false positives: description is probably focused enough.
- High pass rate + high false positives: description likely overreaches.
- Low pass rate + low false positives: description is precise but too narrow.
- Low pass rate + high false positives: description is both unclear and noisy.

When sibling-skill overlap appears, tighten trigger phrases, reduce generic wording, and add more negative boundary tests.
