# Mirurain _(mi-ru-ra-in)_

[![Hosted on Kemonoforge](https://img.shields.io/badge/Hosted_on-Kemonoforge-%23a77d88?style=for-the-badge&logoSize=auto&labelColor=%23657b69&color=%23abd0b2)](https://forge.kemonomimi.moe/OtakuEmily/mirurain)
![Made by Humans](https://img.shields.io/badge/Made_by-Humans-%23a77d88?style=for-the-badge&logoSize=auto&labelColor=%23657b69&color=%23abd0b2)
![Latest PyPI version](https://img.shields.io/pypi/v/Django?style=for-the-badge&labelColor=%23657b69&color=%23abd0b2)

## What is it?

Mirurain is an easy-to-use [Stoat.chat](https://stoat.chat) bot that aggregates
content from [Bluesky](https://github.com/bluesky-social),
[Mastodon](https://github.com/mastodon),
[Nostr](https://github.com/nostr-protocol/nostr), and
[Tumblr](https://github.com/tumblr).

## Configuration

| Scope         | Variable                     | Description                                                                                                                                    | Default                        |
| ------------- | ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------ |
| Stoat         | `MIRURAIN_STOAT_API_KEY`     | The API key to use when authenticating with Stoat.chat                                                                                         |                                |
| Stoat         | `MIRURAIN_STOAT_IS_BOT`      | Whether the connection is as a user or a bot.                                                                                                  | `true`                         |
| Database      | `MIRURAIN_DATABASE_URI`      | The database Mirurain will use; any database URI supported by Tortoise ORM is accepted                                                         |                                |
| Bluesky       | `MIRURAIN_BLUESKY_ENABLED`   | Whether the Bluesky provider should be enabled.                                                                                                | `false`                        |
| Bluesky       | `MIRURAIN_BLUESKY_INSTANCE`  | The Bluesky PDS to use.                                                                                                                        | `https://bsky.social`          |
| Bluesky       | `MIRURAIN_BLUESKY_JETSTREAM` | The Jetstream instances that Mirurain will listen to.                                                                                          | Official bsky.social instances |
| Bluesky       | `MIRURAIN_BLUESKY_USERNAME`  | The username of the account that Mirurain will manage.                                                                                         |                                |
| Bluesky       | `MIRURAIN_BLUESKY_PASSWORD`  | The password of the account that Mirurain will manage.                                                                                         |                                |
| Mastodon      | `MIRURAIN_MASTODON_ENABLED`  | Whether the Mastodon provider should be enabled.                                                                                               | `false`                        |
| Mastodon      | `MIRURAIN_MASTODON_INSTANCE` | The Mastodon instance that Mirurain will interact with.                                                                                        | `https://mastodon.social`      |
| Mastodon      | `MIRURAIN_MASTODON_USERNAME` | The username of the account that Mirurain will manage.                                                                                         |                                |
| Mastodon      | `MIRURAIN_MASTODON_PASSWORD` | The password of the account that Mirurain will manage.                                                                                         |                                |
| Nostr         | `MIRURAIN_NOSTR_ENABLED`     | Whether the Nostr provider should be enabled.                                                                                                  | `false`                        |
| Nostr         | `MIRURAIN_NOSTR_RELAYS`      | The Nostr relays to listen to. Must support NIP-1.                                                                                             |                                |
| OpenTelemetry | `OTEL_`                      | OpenTelemetry configuration, read our exporter's options [here](https://opentelemetry-python.readthedocs.io/en/latest/exporter/otlp/otlp.html) |                                |

## TODO

# Beta

- [ ] Add some type of native third-party provider support.
- [ ] Implement Tumblr provider - Blocked by Alpha.
- [ ] Implement project "UI" localisation and investigate support for BYOT post translation.

## Alpha

- [ ] Implement Mastodon provider - Blocked by `Provider`
- [ ] Implement Bluesky provider - Blocked by `Provider`
- [ ] Implement Nostr provider - Blocked by `Provider`
- [x] Implement the `Provider` class
- [x] Implement fanning - partially completed, but it needs error handling and a general clean-up. It also needs refactoring to move the runner into a dedicated task instead of a start-up event.
- [x] Implement core bot setup - partially completed, but `app.py` is incomplete and still has testing logic. The bot's core framework needs clean-up and general improvements.

## AI in Our Codebase

The Mirurain project has the goal of ethical usage of AI in our codebase; therefore we restrict the usage of AI to;

- Codebase reviews through tools like CodeRabbit.
- Improving documentation strings of new code.
- Get recommendations on how an idea may be implemented, this type of usage should ALWAYS be treated as just guidance unless you have an understanding of the topic.

AI will NEVER be used to directly edit the project's _logic_ and any changes by AI such as _documentation improvements_ must be reviewed by the submitter, and signs of vibe-coded changes may result in pull requests being blocked to protect our codebase from AI-generated code.

Commits signed by Codex, Claude, or any other AI harnesses will be heavily scrutinised and possibly blocked, these harnesses by themselves do not provide enough measures to review changes by agents and therefore direct commits from them are treated as dangerous.
