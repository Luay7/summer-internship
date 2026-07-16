# CLI Broken Link Checker

## Day 5: Ship and Reflect

The goal of Day 5 is to complete the project, improve the current application, test all features, and prepare the project for final submission.

The project will continue from the Day 2 implementation instead of being rebuilt from scratch.

The Day 2 version, `v0.3.0`, will be used as the baseline. The improvements found during the Day 3 code review will be added gradually through multiple versions.

Each version will be tested before moving to the next version.

## Version v0.4.0 — Clear Error Handling and Link Extraction

This version improves the readability of the existing code without changing its main behavior.

### Improvements

* Added separate handling for timeout, HTTP, connection, and unexpected network errors.
* Simplified link extraction by selecting only anchor tags with a valid `href`.

### Testing

* Valid URL scan: Passed.
* Invalid URL validation: Passed.
* Connection error handling: Passed.
* HTTP error handling: Passed.
* Full link verification: Passed.

## Version v0.5.0 — Link Accuracy and Efficiency

This version improves how links are stored and checked.

### Improvements

* Removed URL fragments before checking links.
* Replaced the link list with a `set`.
* Prevented duplicate links from being checked more than once.
* Updated the link count to show only unique valid links.

### Testing

A local test page was created with seven link elements. Some links were duplicated, and some contained URL fragments.

After cleaning and filtering the links, the program correctly found and checked only three unique links.

* URL fragment removal: Passed.
* Duplicate link filtering: Passed.
* Unique link count: Passed.
