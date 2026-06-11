# jmat50.github.io

Personal landing page for [jmat50.github.io](https://jmat50.github.io), built with Jekyll and hosted on GitHub Pages.

## Projects

Project cards are driven by [`_data/projects.yml`](_data/projects.yml). To add a new project, append an entry:

```yaml
- name: My New Project
  description: Short summary shown on the card.
  language: Python
  repo: https://github.com/Jmat50/my-new-project
  demo: /optional/live-demo-path.html   # omit if no demo
  tags:
    - tag-one
    - tag-two
```

## Local development

Requires Ruby and Bundler:

```bash
bundle install
bundle exec jekyll serve
```

Open [http://localhost:4000](http://localhost:4000).

## Deployment

Push to the `main` branch of this repository. GitHub Pages builds the Jekyll site automatically.

## Automatic project sync

The [Sync projects](.github/workflows/sync-projects.yml) workflow runs every 6 hours (and on demand) to detect new **public** repositories on your GitHub account. It appends them to `_data/projects.yml` using the same card fields as existing entries:

- `description` from the repo (or a short fallback)
- `language` from GitHub
- `tags` from repo topics, or language + `open-source`
- `demo` from the repo homepage, or known overrides like GameDudeSynth and extreme-checkers

Existing entries are never overwritten, so you can keep custom copy, tags, and demo links. To run it immediately: **Actions → Sync projects → Run workflow**.

## GameDudeSynth demo

The `GameDudeSynth/` folder contains a static copy of the live demo, deployed from the [GameDudeSynth](https://github.com/Jmat50/GameDudeSynth) source repo. Edit that project in its own repository, not here. That deploy updates only `GameDudeSynth/` and must not remove `index.html` or add `.nojekyll`, or the Jekyll landing page will stop working.
