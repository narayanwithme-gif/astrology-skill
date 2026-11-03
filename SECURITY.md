# Security and private data

Birth requests and generated reports can contain identifying information. Keep personal requests in `private/` and generated reports in `reports/`; both directories are ignored by Git. The committed example is fictional. Inspect files before uploading an archive or opening a pull request: `.gitignore` does not remove data from an existing commit.

The calculator runs locally and does not upload requests. Dependencies are downloaded during setup. Hermes may send conversation content and tool results to its configured model provider; consult that provider's settings before supplying personal data.

For an ordinary bug, open a GitHub issue with fictional input and the error message. For a security issue, use GitHub's private vulnerability reporting if enabled for the repository. If it is unavailable, ask the maintainer for a private contact channel without posting exploit details, credentials or personal data publicly.

Only reviewed dependency releases should be added to the pinned requirements. Do not attach real birth profiles, access tokens or full environment dumps to reports.
