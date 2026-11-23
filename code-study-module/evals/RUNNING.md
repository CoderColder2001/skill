# Behavioral evaluation

`evals.json` uses the skill-creator schema: `id`, `prompt`, `expected_output`, `files`, and independently graded `expectations`. Fixture paths are relative to the skill root. These are source-reading examples, not production integrations.

## Run a case

1. Create a fresh isolated project directory outside any containing Git repository. For each listed fixture, copy its path relative to `fixtures/mini_repo/` or `fixtures/ambiguous_repo/` into that directory, preserving nested paths. Do not copy unrelated fixtures or previous outputs.
2. Give the evaluator only the candidate skill (and its referenced resources), the project location, and the case's exact prompt. Run in that project. Do not give it `expected_output`, `expectations`, this guide, or earlier conclusions. For case 8, supply the skill location as the available local skill.
3. For trigger cases 7 and 8, expose the skill as available for selection; do not instruct the evaluator to invoke it. For case 2, use an empty project.
4. Save the actual output/document and transcript outside the installed skill. Grade each expectation against observed behavior and source evidence. A request for input is the expected terminal outcome for cases 2 and 6; do not invent a user reply.
5. Check local link resolution, cited symbols/lines, path/language, factual accuracy, and unwanted actions. Evaluate meaning, not an exact heading or wording. A source file existing alone does not prove a claim.

Use a new project for each run, including repeat runs. Keep the skill version, case ID, environment, pass/fail evidence, and observed limitations with results. Report exactly which cases ran; JSON validation is not a behavioral pass, and one successful run does not establish stability.

The default fixture projects are non-Git directories. A separate metadata variant can use an existing disposable repository with known HEAD and uncommitted source changes; assert that the document reports the actual revision and distinguishes those changes. Do not create commits or modify a real repository merely to prepare this variant without authorization.
