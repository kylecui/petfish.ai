# Instructions

This directory contains behavior contracts for the ChatGPT Custom GPT surface.

These files are not ordinary documentation. They define how PEtFiSh Companion GPT should behave.

## Files

| File | Purpose |
|---|---|
| `petfish-companion.instructions.md` | main GPT instruction body |
| `safety-boundary.md` | execution truth and risk boundaries |
| `answer-contract.md` | output shapes for common task classes |
| `anti-sycophancy.md` | critical review discipline |

## GPT Builder usage

The main GPT Instructions field should include the main instruction body and a concise merge of the safety, answer, and anti-sycophancy contracts.

Do not upload these files as Knowledge only. If they are only in Knowledge, they may be retrieved inconsistently and will not reliably govern behavior.

## Update rule

Any change to these files should be paired with eval updates when it affects:

- routing;
- safety boundaries;
- remote execution claims;
- pack recommendation behavior;
- anti-sycophancy behavior.
