# Changelog

## [2.0.0](https://github.com/PatelFarhaan/authgate/compare/v1.0.9...v2.0.0) (2026-04-13)


### ⚠ BREAKING CHANGES

* add is_active flag to disable user login  Adds is_active boolean to users table (default true). Enforced in  the OAuth callback, /api/verify, and /api/userinfo — disabled users  cannot log in and active JWTs are invalidated.  BREAKING CHANGE: existing deployments must run  ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE;  before upgrading.
* remove deprecated provider columns, return providers list  Deletes User.provider and User.provider_id columns and switches  UserInfo to return providers: list[str] sourced from the UserProvider  relationship, sorted most-recently-linked first.  BREAKING CHANGE: UserInfo.provider (string) replaced with UserInfo.providers (list[str]).  API consumers must update their parsing. Existing user.provider and user.provider_id  columns in the users table are now unused — safe to drop.

### Features

* add is_active flag to disable user login  Adds is_active boolean to users table (default true). Enforced in  the OAuth callback, /api/verify, and /api/userinfo — disabled users  cannot log in and active JWTs are invalidated.  BREAKING CHANGE: existing deployments must run  ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE;  before upgrading. ([90c146a](https://github.com/PatelFarhaan/authgate/commit/90c146a880a367e2df7cee36d4d61991ba382539))
* **api:** add user account disabling feature ([ef1bfba](https://github.com/PatelFarhaan/authgate/commit/ef1bfba94481693f8cc1340b77b5686d001fe6af))
* redesign login page with shield logo, light/dark themes, and screenshots ([ee6cf0c](https://github.com/PatelFarhaan/authgate/commit/ee6cf0cd3c72a350fbf5337449354904a1dd88e3))
* remove deprecated provider columns, return providers list  Deletes User.provider and User.provider_id columns and switches  UserInfo to return providers: list[str] sourced from the UserProvider  relationship, sorted most-recently-linked first.  BREAKING CHANGE: UserInfo.provider (string) replaced with UserInfo.providers (list[str]).  API consumers must update their parsing. Existing user.provider and user.provider_id  columns in the users table are now unused — safe to drop. ([44559be](https://github.com/PatelFarhaan/authgate/commit/44559be701f8574ad990adfb8404c75e771c439c))
* update login page styles and enhance configuration for accent color ([ef4b318](https://github.com/PatelFarhaan/authgate/commit/ef4b31873e6e98a0d6ca5eb1d9c1cb217dfa3a93))
