# `action-version`

OrgWarden maintains two sets of semantic version tags - one for the [OrgWarden CLI tool](../src) (ex: `v0.1.2`), and one for the [OrgWarden composite action](../action.yml) (ex: `action-v0.2.3`).

The [CD workflow](../.github/workflows/CD.yml) uses [`AutoGitSemVer`](https://github.com/davidbrownell/AutoGitSemVer) to analyze changes to the CLI & composite action source code and independently update their respective tags accordingly. Due to a quirk with `AutoGitSemVer`, this `action-version` directory is required in order to analyze changes to the `action.yml` file. As such, this directory should not contain any files other than this `README.md` and the [`AutoGitSemVer.yml`](./AutoGitSemVer.yml) configuration file.

For context on how this directory is used with `AutoGitSemVer`, see the [`update_tags.sh` script](../.github/update_tags.sh).