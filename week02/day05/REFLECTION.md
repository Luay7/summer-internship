# Final Reflection

## AI-Assisted Development Experience

This project showed me that AI can speed up software development, but its output still needs to be reviewed, tested, and improved manually.

### Where AI Helped

AI helped me turn the original project idea into a clear software specification and build the first working CLI version step by step.

It was useful for:

* Creating the initial command-line structure.
* Adding URL validation and network requests.
* Extracting and checking links.
* Explaining unfamiliar code.
* Reviewing the generated code and suggesting improvements.
* Diagnosing the intentionally introduced bugs.
* Improving the fallback strategy and organizing the final code into functions.
* Creating repeatable local and Docker tests.

During Day 4, AI correctly helped diagnose five intentionally introduced bugs related to CLI arguments, URL validation, duplicate links, unrealistic timeout values, and missing request timeouts.

### Where AI Needed Verification

The first AI-generated version worked, but it still had several weaknesses.

It used general error handling, checked duplicate links inefficiently, treated URL fragments as separate links, and only used the GET fallback for a limited number of HEAD responses.

Some network failures were also classified as dead links even when no HTTP status was received. The Day 4 output showed how incorrect timeout values could create many false results and make valid links appear broken.

AI also sometimes suggested completing too many improvements at once. I had to slow the process down and apply the changes through separate versions so that every improvement could be tested and documented clearly.

### Manual Intervention

Manual work was necessary to:

* Keep the project within the original scope.
* Review the code line by line.
* Decide which improvements should be applied in each version.
* Run every test and compare the actual result with the expected result.
* Create a deterministic local test server instead of depending only on public websites.
* Fix local server and Docker networking issues.
* Verify all available decision branches in the final code.
* Confirm that all 18 timeout and error branch tests passed inside Docker.
* Organize the GitHub history using clear versions and commits.

### What I Learned

The most effective workflow was a combination of specification-first development and iterative refinement.

The specification kept the project focused, while the version-by-version process made each change easier to understand and verify.

I also learned that working code is not automatically correct code. AI suggestions should be treated as a starting point, not as a final answer. Error messages, test results, and code review were more reliable than simply trusting generated code.

Overall, AI was most helpful as a pair-programming and debugging partner. The final responsibility for correctness, testing, and project decisions still required manual judgment.


