# Upload to GitHub

Suggested repository name: `hermes-astrology`.

Suggested description: `Western and Jyotisha chart calculations and reading workflows for Hermes.`

## Browser upload

1. Create an empty GitHub repository. Do not add a separate README or license.
2. Extract the source ZIP.
3. Upload the contents of `hermes-astrology`, including `.github`, `.gitignore` and `.gitattributes`, to the repository root. Some file pickers hide dotfiles; check the selection.
4. Commit the files and open the Actions tab to review the checks.

If the browser uploader omits hidden files, use Git instead.

## Upload with GitHub CLI

From the prepared repository folder, authenticate with your own GitHub account, then run:

```sh
gh repo create hermes-astrology --public --source . --remote origin --push
```

Use `--private` instead of `--public` for a private repository. Do not put access tokens in shell commands or files.

The source ZIP excludes `.git`. After extracting that ZIP, create the initial commit before using the command above:

```sh
git init -b main
git add .
git commit -m "Initial release"
```

## After upload

- Confirm the license is detected and Actions passes on GitHub. The local checks do not establish that the hosted matrix has run.
- Add repository topics such as `hermes-agent`, `agent-skills`, `astrology`, `jyotisha` and `python`.
- Enable private vulnerability reporting if you intend to maintain the public repository.
- Create a `v1.0.0` release when ready. Build distribution files with `python -m build`; attach only files you have inspected for personal data.
