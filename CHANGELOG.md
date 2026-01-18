# CHANGELOG


## v0.19.1 (2026-01-18)


## v0.19.0 (2026-01-18)

### Bug Fixes

- Refactor `return run execute: ...` -> `return: ...`
  ([`ea87153`](https://github.com/rx-modules/bolt-expressions/commit/ea8715367814c839815e04d2b985af5b1fa44bcf))

### Chores

- Change to uv ([#91](https://github.com/rx-modules/bolt-expressions/pull/91),
  [`8be6518`](https://github.com/rx-modules/bolt-expressions/commit/8be6518d5ad7d46c41b5ecdd789563fa54b33693))

* chore: change to uv

* chore: format imports

---------

Co-authored-by: rx97 <rx97>

- Fix up ci/cd
  ([`a1ad593`](https://github.com/rx-modules/bolt-expressions/commit/a1ad5931a114b59dcf3d1a725dff3a813c6c75ec))

- Try again agian
  ([`cb31579`](https://github.com/rx-modules/bolt-expressions/commit/cb3157948deed3ace02c09ee33f678675000d2fc))

- Try agian
  ([`39c3065`](https://github.com/rx-modules/bolt-expressions/commit/39c3065c50aad2b7509c7927ee5651268715a78a))

### Features

- Latest empty push attempt
  ([`d758bc8`](https://github.com/rx-modules/bolt-expressions/commit/d758bc81d524e22a5537bfbd1c4f732c07d01f15))

- Update to 3.14, newest beet/bolt ([#92](https://github.com/rx-modules/bolt-expressions/pull/92),
  [`bfae638`](https://github.com/rx-modules/bolt-expressions/commit/bfae638796fbd2fec4b76f4e462865a02d8657f1))

* feat: fix up examples, linting, and more

* fixes using tellraw with Sources

* chore: fix up gh action

* chore: fix pyproject.toml version lookup

* chore: fix up pyproject st uff

* chore: update rich

* chore: git checkout

* chore: condition to semantic release


## v0.18.0 (2025-01-28)

### Features

- Add temp_score_prefix and const_score_prefix options
  ([`32a0ab6`](https://github.com/rx-modules/bolt-expressions/commit/32a0ab64d4f1b4971e4a4913c60ad14e49319e4e))


## v0.17.1 (2025-01-27)

### Bug Fixes

- Set rich as normal dependency
  ([`7f39b2a`](https://github.com/rx-modules/bolt-expressions/commit/7f39b2a36067dca27f9a7d29c8d038e4ab225fdc))


## v0.17.0 (2024-08-10)

### Bug Fixes

- Contrib.commands failed to parse data sources with empty path
  ([`3663d96`](https://github.com/rx-modules/bolt-expressions/commit/3663d9613e9cc4f5ad9b145859c82de332d47f06))

- Improve source reuse optimization
  ([`6f1aef7`](https://github.com/rx-modules/bolt-expressions/commit/6f1aef79f6356015b7f20edabdb60fa0d6c542a3))

- Make nbt_type argument of Data.cast optional
  ([`beca595`](https://github.com/rx-modules/bolt-expressions/commit/beca595b0c37a9d7c427b3fe22160fd86e640baa))

- Type checking failing for expandable compound types
  ([`3b8c57e`](https://github.com/rx-modules/bolt-expressions/commit/3b8c57edd4a6a444109f89acbc01d2862e224e84))

### Chores

- Update dependencies
  ([`6d1ae18`](https://github.com/rx-modules/bolt-expressions/commit/6d1ae183807074b6fa3ab52075327bb2977f15af))

### Code Style

- Paint it black
  ([`b8a702b`](https://github.com/rx-modules/bolt-expressions/commit/b8a702b9950ea43263721d865dc9bf6ce7a0c73e))

### Features

- Add composite literals
  ([`ae424a1`](https://github.com/rx-modules/bolt-expressions/commit/ae424a157322090ecd244065e554ef4c83e43dee))

- Make Data.cast lazy
  ([`4d4e739`](https://github.com/rx-modules/bolt-expressions/commit/4d4e739e64c1542f62f5cb3350717913beb35fa4))

### Testing

- Add composite_literal
  ([`52529b0`](https://github.com/rx-modules/bolt-expressions/commit/52529b06de052de1e1c1bf09548def56bb1fc521))

- Update tests
  ([`a5d39de`](https://github.com/rx-modules/bolt-expressions/commit/a5d39decc6f3d0e26c39d09828485909a3a104c9))


## v0.16.1 (2024-06-23)

### Bug Fixes

- Remove scientific notation formatting for small scale numbers
  ([`e72080d`](https://github.com/rx-modules/bolt-expressions/commit/e72080d2ffada4fd6c4adc912b90e08a84569505))

### Chores

- Update poetry lock
  ([`8bf0eac`](https://github.com/rx-modules/bolt-expressions/commit/8bf0eacd9ea46d377664165638003d087854d860))


## v0.16.0 (2024-02-23)

### Bug Fixes

- Add store result inlining rule
  ([`006750b`](https://github.com/rx-modules/bolt-expressions/commit/006750bfb95d2ab1c29a95d21e3204c599d8405a))

- Lazy sources should discard previous value when reused
  ([`2101335`](https://github.com/rx-modules/bolt-expressions/commit/2101335ad560208d2f2f38959f5ea8966c5baf80))

### Code Style

- Paint it black
  ([`3447f73`](https://github.com/rx-modules/bolt-expressions/commit/3447f73ce8076cbd09fab7376b16811fd5d35736))

### Features

- Add string data source indexing and slicing
  ([`4b5fa58`](https://github.com/rx-modules/bolt-expressions/commit/4b5fa58cb83efdc6fcfadc3f270631786b7c1298))

- Overloaded len function for data sources
  ([`792657b`](https://github.com/rx-modules/bolt-expressions/commit/792657baa2de8c9f5d88c8e15c22363d97550ce6))


## v0.15.0 (2024-02-16)

### Bug Fixes

- Strip run execute from commands
  ([`c8648f2`](https://github.com/rx-modules/bolt-expressions/commit/c8648f229aa2201384d91d0bbcb7a9864133c4b9))

### Chores

- Set vscode default interpreter path
  ([`62e86c3`](https://github.com/rx-modules/bolt-expressions/commit/62e86c3686a2d27bedf13e499b3f3f7fa3a50d70))

### Code Style

- Paint it black
  ([`a2ae2f3`](https://github.com/rx-modules/bolt-expressions/commit/a2ae2f33639f1ca9bcfaea10fc567ff1144a6070))

### Features

- Add and/or operator support for sources/lazy sources
  ([`f8013e9`](https://github.com/rx-modules/bolt-expressions/commit/f8013e94feac584b470ebbadeb861423b24c4416))

- Add source branching and comparison operators
  ([`f8d8ec4`](https://github.com/rx-modules/bolt-expressions/commit/f8d8ec4b3612d080e17808e0a9bf02d3256a3f23))

- Data comparison operator
  ([`749dd79`](https://github.com/rx-modules/bolt-expressions/commit/749dd79b6e96c4bec0fa79eaff9733982e1649c5))

- Improved if..elif..else with __multibranch__
  ([`1746226`](https://github.com/rx-modules/bolt-expressions/commit/174622679945b3b09634316e212036d195eb51e6))

### Refactoring

- Replace IrSerializer with AstConverter, require Context object
  ([`f6c4d82`](https://github.com/rx-modules/bolt-expressions/commit/f6c4d823e737ff590c46cc85bcffb5114c532e0f))

### Testing

- Add operation_condition, update tests
  ([`fabf619`](https://github.com/rx-modules/bolt-expressions/commit/fabf619f980cb8927e59694f8744eeeda90dc15b))


## v0.14.0 (2024-02-05)

### Bug Fixes

- Only cast numeric nbt types
  ([`86d49b1`](https://github.com/rx-modules/bolt-expressions/commit/86d49b1b257996ded2c5becef223c9e6806b3c6a))

### Chores

- Add frozendict dependency
  ([`8051e6f`](https://github.com/rx-modules/bolt-expressions/commit/8051e6fa83294b762f354442ccd6fd14c5aa3425))

- Update vscode settings
  ([`1d12397`](https://github.com/rx-modules/bolt-expressions/commit/1d123978265343cbedf9e10cbb3291b1e07159a0))

### Code Style

- Paint it black
  ([`86bf28a`](https://github.com/rx-modules/bolt-expressions/commit/86bf28a4fa9acd989a9caf9f3271c190817922ac))

### Features

- Literal casting
  ([`9874ca9`](https://github.com/rx-modules/bolt-expressions/commit/9874ca91f2c7045ffc8fbf17b06505984f2870c2))

- Separate data source interfaces for each nbt type
  ([`dbe9a74`](https://github.com/rx-modules/bolt-expressions/commit/dbe9a74f31f3c58fb1b34a5069edada983535ec9))

- Source lazy values and data source operator handlers
  ([`6832b91`](https://github.com/rx-modules/bolt-expressions/commit/6832b9173d15ae6a88dd9d7d5b21929b459e41e6))

- Support dicts, lists, arrays and union types
  ([`1097f5f`](https://github.com/rx-modules/bolt-expressions/commit/1097f5fedf8a7211c5437deeeac50eadd256ae03))

- Type checking
  ([`b031303`](https://github.com/rx-modules/bolt-expressions/commit/b0313037e4428dd5e41cc7c608931cf613c6701f))

### Testing

- Fix inheritance and typing, update snapshots
  ([`9930a26`](https://github.com/rx-modules/bolt-expressions/commit/9930a2662d50e8f72ce0c65f912a6105180e1ab7))


## v0.13.1 (2024-01-24)

### Bug Fixes

- Remove rich import
  ([`a07da7d`](https://github.com/rx-modules/bolt-expressions/commit/a07da7d539b1d0289d539d82493de8ed465d9e28))


## v0.13.0 (2024-01-23)

### Bug Fixes

- Make api not dependent of Context object
  ([`72afafe`](https://github.com/rx-modules/bolt-expressions/commit/72afafe6f317147918ae95641a586c8f70b2ca2a))

- Reduce number of temporaries used for score and data operations
  ([`8756e50`](https://github.com/rx-modules/bolt-expressions/commit/8756e50002052b255bf6c2c1ccabb29271b93ef0))

- Reuse temporary score names
  ([`0eb9556`](https://github.com/rx-modules/bolt-expressions/commit/0eb9556918d9b0b1c0dbafe68a872763347f58ec))

### Chores

- Update poetry lock
  ([`2b31803`](https://github.com/rx-modules/bolt-expressions/commit/2b318032c5325e95562646d4711f56585c19155d))

### Code Style

- Paint it black
  ([`2eddff5`](https://github.com/rx-modules/bolt-expressions/commit/2eddff53b6bdf88b84baf76411dfaa72cda694f3))

- Paint it black
  ([`61208fe`](https://github.com/rx-modules/bolt-expressions/commit/61208fe8d04d48fca74e768d5ccab246c48560ab))

### Features

- Specify data source types using square brackets
  ([`b7b96fb`](https://github.com/rx-modules/bolt-expressions/commit/b7b96fb9c01580bd9504274f8728d1eea4ff1c28))

### Refactoring

- Implement optimizer IR
  ([`690eb40`](https://github.com/rx-modules/bolt-expressions/commit/690eb409837c6401a52fc2ec2c9b8ba181cdeb70))

- Implement serializer
  ([`8252db4`](https://github.com/rx-modules/bolt-expressions/commit/8252db4ad2bd5f03d169b6646b6730a254f5769d))

- Injected api using attribute handler
  ([`0297354`](https://github.com/rx-modules/bolt-expressions/commit/0297354d6e1d37298bc727a05c7dbbdea6ad1835))

- Moved Expression api to node.py, major node operator changes
  ([`add0eda`](https://github.com/rx-modules/bolt-expressions/commit/add0eda4cf4879c2ed815381b56f40ba8619ae9d))

also tweaked plugin.py and temporarely removed the api auto-injection

- Optimizer as instance and fix smart generator typing
  ([`a39000f`](https://github.com/rx-modules/bolt-expressions/commit/a39000fdfea89791798d74b425fdbbceb66420b4))

- Remove resolver
  ([`230f5a1`](https://github.com/rx-modules/bolt-expressions/commit/230f5a1531186400732a9ea8e37e35e6815b5136))

- Score/data tuples, resolve and operators can return results, fixed min/max functions
  ([`4fe07ed`](https://github.com/rx-modules/bolt-expressions/commit/4fe07eddc892e8e12cf99567ffe1b05d83dea4d2))

### Testing

- Fix pack format
  ([`ac6ee95`](https://github.com/rx-modules/bolt-expressions/commit/ac6ee95bda067e28350a3ffdf4dbfafe245b7e37))

- Update operation_nbt_type
  ([`c2b27d4`](https://github.com/rx-modules/bolt-expressions/commit/c2b27d4296a576bf57b8f091c6ee89e6b840e757))

- Update tests
  ([`3d0c760`](https://github.com/rx-modules/bolt-expressions/commit/3d0c760f19b022fc421f3edcbf5d0de21120b235))


## v0.12.2 (2023-01-08)

### Bug Fixes

- Fix inheritance of expression nodes and dataclasses.replace
  ([`bd6ac3d`](https://github.com/rx-modules/bolt-expressions/commit/bd6ac3d478a255603f2d70670337dd158fbefeaf))

### Chores

- **deps**: Bump beet from 0.79.2 to 0.82.1
  ([#73](https://github.com/rx-modules/bolt-expressions/pull/73),
  [`a4ee343`](https://github.com/rx-modules/bolt-expressions/commit/a4ee3439ce47c0471ca541ab923beb1f552d088e))

Bumps [beet](https://github.com/mcbeet/beet) from 0.79.2 to 0.82.1. - [Release
  notes](https://github.com/mcbeet/beet/releases) -
  [Changelog](https://github.com/mcbeet/beet/blob/main/CHANGELOG.md) -
  [Commits](https://github.com/mcbeet/beet/compare/v0.79.2...v0.82.1)

--- updated-dependencies: - dependency-name: beet dependency-type: direct:production

update-type: version-update:semver-minor ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump mecha from 0.59.2 to 0.60.3
  ([#66](https://github.com/rx-modules/bolt-expressions/pull/66),
  [`384ee09`](https://github.com/rx-modules/bolt-expressions/commit/384ee09fddbd2bd6c98caa17e6afe3b8d99d331e))

Bumps [mecha](https://github.com/mcbeet/mecha) from 0.59.2 to 0.60.3. - [Release
  notes](https://github.com/mcbeet/mecha/releases) -
  [Changelog](https://github.com/mcbeet/mecha/blob/main/CHANGELOG.md) -
  [Commits](https://github.com/mcbeet/mecha/compare/v0.59.2...v0.60.3)

--- updated-dependencies: - dependency-name: mecha dependency-type: direct:production

update-type: version-update:semver-minor ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps-dev**: Bump black from 22.10.0 to 22.12.0
  ([#68](https://github.com/rx-modules/bolt-expressions/pull/68),
  [`95895ea`](https://github.com/rx-modules/bolt-expressions/commit/95895eabb31d36535616039ef3e7ff4f2f99e1ee))

Bumps [black](https://github.com/psf/black) from 22.10.0 to 22.12.0. - [Release
  notes](https://github.com/psf/black/releases) -
  [Changelog](https://github.com/psf/black/blob/main/CHANGES.md) -
  [Commits](https://github.com/psf/black/compare/22.10.0...22.12.0)

--- updated-dependencies: - dependency-name: black dependency-type: direct:development

update-type: version-update:semver-minor ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

Co-authored-by: TheWii <67249660+TheWii@users.noreply.github.com>

- **deps-dev**: Bump isort from 5.10.1 to 5.11.4
  ([`ff7c5b1`](https://github.com/rx-modules/bolt-expressions/commit/ff7c5b1433ce0d97bf9a44ace069e0ef857e0754))

Bumps [isort](https://github.com/pycqa/isort) from 5.10.1 to 5.11.4. - [Release
  notes](https://github.com/pycqa/isort/releases) -
  [Changelog](https://github.com/PyCQA/isort/blob/main/CHANGELOG.md) -
  [Commits](https://github.com/pycqa/isort/compare/5.10.1...5.11.4)

--- updated-dependencies: - dependency-name: isort dependency-type: direct:development

update-type: version-update:semver-minor ...

Signed-off-by: dependabot[bot] <support@github.com>


## v0.12.1 (2022-12-31)

### Bug Fixes

- Preserve key/default logic of builtin min/max functions
  ([`c127114`](https://github.com/rx-modules/bolt-expressions/commit/c127114beefff5e392cc3e4733b7c113202ccf91))


## v0.12.0 (2022-12-30)

### Bug Fixes

- Make wrapped min/max functions behave more like the builtin ones
  ([`7e3b400`](https://github.com/rx-modules/bolt-expressions/commit/7e3b4003e677bf7a1bd9c4728f332f63e6a12081))

- Remove commands that multiply/divide by 1, add/subtract by 0
  ([`6d8cf88`](https://github.com/rx-modules/bolt-expressions/commit/6d8cf882b029d49b120116ed088ee395d3902132))

### Features

- Support literal floating numbers on score multiplication/division
  ([`eea20d4`](https://github.com/rx-modules/bolt-expressions/commit/eea20d4d6a587e278f0a8bf8a7cae3a431b00fdd))

### Refactoring

- Add ScoreOperation base class
  ([`b0626c1`](https://github.com/rx-modules/bolt-expressions/commit/b0626c1c2f0cedc7af3d73e8089f38637f39da83))

- Late conversion of literals into score constants
  ([`5713b30`](https://github.com/rx-modules/bolt-expressions/commit/5713b3071fc9f2e845021fd0243d67d165d68bec))


## v0.11.2 (2022-12-27)

### Bug Fixes

- Import all subpackages in __init__ for conveniency
  ([`7c2ed2c`](https://github.com/rx-modules/bolt-expressions/commit/7c2ed2c65d80b1e0f91efd970724414c24fd3e91))


## v0.11.1 (2022-12-27)

### Bug Fixes

- Generate negative score constants in init function
  ([`9ec47cb`](https://github.com/rx-modules/bolt-expressions/commit/9ec47cb3b7aa4e1d0baf865a2fa29a902eae1790))


## v0.11.0 (2022-11-19)

### Features

- Add `component` method to convert sources into text components
  ([`a22caf9`](https://github.com/rx-modules/bolt-expressions/commit/a22caf9256c234944ff1de41829d48e7c37ddc9b))

- Implicitly convert sources into text components
  ([`d27870e`](https://github.com/rx-modules/bolt-expressions/commit/d27870ef068b27dddf054b01d6c418d608a0a61a))

### Testing

- Add source_component
  ([`0033426`](https://github.com/rx-modules/bolt-expressions/commit/003342603ae28a86f46800b4ec39f5d4a9681c3c))


## v0.10.0 (2022-11-15)

### Chores

- Update dependencies
  ([`8cbd7a0`](https://github.com/rx-modules/bolt-expressions/commit/8cbd7a041c464f88050f5a50fc0d64b520a97559))

### Features

- Add bolt_expressions.contrib.commands
  ([`e40ae95`](https://github.com/rx-modules/bolt-expressions/commit/e40ae9562bae5589a0c541a60884ce79211febf8))

- Require bolt_expressions.contrib.commands by default
  ([`f748ee3`](https://github.com/rx-modules/bolt-expressions/commit/f748ee3ea2e6cc5eb9416d295ce39001d03856da))

### Testing

- Add contrib_commands
  ([`7ff0871`](https://github.com/rx-modules/bolt-expressions/commit/7ff08712fd53751c4af218eb6fd2da9d5fcad124))


## v0.9.0 (2022-11-07)

### Code Style

- Paint it black
  ([`adb96ad`](https://github.com/rx-modules/bolt-expressions/commit/adb96ad3819de7ce7bb9c188044ed53305ef6e48))

### Features

- Let custom objectives be added to init function
  ([`99483fb`](https://github.com/rx-modules/bolt-expressions/commit/99483fbbcd4c3653b40cc3eed0c948843699caea))


## v0.8.3 (2022-11-07)

### Bug Fixes

- Generate init function only when needed
  ([`01f3193`](https://github.com/rx-modules/bolt-expressions/commit/01f3193d56d79c62608ff239b8f26032c1cc2685))

- Prevent init function from having duplicated/unused constants
  ([`05a2638`](https://github.com/rx-modules/bolt-expressions/commit/05a2638a8e9f637f443b2a98419544b3abd75127))

- Prevent init function from having unused objectives
  ([`4b6a490`](https://github.com/rx-modules/bolt-expressions/commit/4b6a490b47345e5ee66e386c839aebc052c22ac4))

### Testing

- Update snapshots
  ([`aec87a9`](https://github.com/rx-modules/bolt-expressions/commit/aec87a993320072fb80a3fbe84304d4a8186d49a))


## v0.8.2 (2022-08-28)

### Bug Fixes

- Datasource._copy doesn't support subclasses.
  ([`21d1db3`](https://github.com/rx-modules/bolt-expressions/commit/21d1db3447061fa5eefcaf60aae8ac9b755e4d5e))

### Chores

- Fix cache setup
  ([`335ec94`](https://github.com/rx-modules/bolt-expressions/commit/335ec94b5273c6700340aba04df0d42656145aef))

- Fix docs mdinclude
  ([`691050e`](https://github.com/rx-modules/bolt-expressions/commit/691050ee11c158e89c61e4b87715a6a425be755e))


## v0.8.1 (2022-08-24)

### Bug Fixes

- Let dicts be used as filter keys in DataSource paths
  ([`f10cbdf`](https://github.com/rx-modules/bolt-expressions/commit/f10cbdfdc334b67d1303f920d9512271ced2a540))


## v0.8.0 (2022-07-27)

### Bug Fixes

- Better nbt type handling
  ([`9f63995`](https://github.com/rx-modules/bolt-expressions/commit/9f63995b4fdfd38803da54260acd18bb09493c45))

- Scaling/casting between data sources doesn't work
  ([`5074414`](https://github.com/rx-modules/bolt-expressions/commit/50744149cf3a16cefce18e42d096ffc44196f1bc))

### Chores

- Update poetry.lock
  ([`3f1b173`](https://github.com/rx-modules/bolt-expressions/commit/3f1b173c82d67a6423042252d4255c3e9e12956f))

### Features

- Api method to cast expressions to any nbt type
  ([`eb3d532`](https://github.com/rx-modules/bolt-expressions/commit/eb3d53227df26d48f8291f1f0137ccc12f75caba))

### Testing

- Nbt type
  ([`e49ad98`](https://github.com/rx-modules/bolt-expressions/commit/e49ad98727105762711290096ed1ec5a5d63fdf1))

- Update conftest.py
  ([`515a3bd`](https://github.com/rx-modules/bolt-expressions/commit/515a3bde0e5e8f01be02742e334b08bc74b1d1d5))

- Update snapshots
  ([`0148d87`](https://github.com/rx-modules/bolt-expressions/commit/0148d87641272416fb64731d90ce90b325ac5dbe))


## v0.7.0 (2022-06-15)

### Chores

- Fix poetry dependencies
  ([`c37687d`](https://github.com/rx-modules/bolt-expressions/commit/c37687d91b730295ab6650befb231dd897963cd5))

- **deps**: Bump beet from 0.63.1 to 0.67.0
  ([`3183ee1`](https://github.com/rx-modules/bolt-expressions/commit/3183ee1804d71ed976311a5bb6ff69bc63743fa7))

Bumps [beet](https://github.com/mcbeet/beet) from 0.63.1 to 0.67.0. - [Release
  notes](https://github.com/mcbeet/beet/releases) -
  [Changelog](https://github.com/mcbeet/beet/blob/main/CHANGELOG.md) -
  [Commits](https://github.com/mcbeet/beet/compare/v0.63.1...v0.67.0)

--- updated-dependencies: - dependency-name: beet dependency-type: direct:production

update-type: version-update:semver-minor ...

Signed-off-by: dependabot[bot] <support@github.com>

- **deps**: Bump beet from 0.67.0 to 0.67.1
  ([`6d5f5e2`](https://github.com/rx-modules/bolt-expressions/commit/6d5f5e241b030bd82de37ee35f3873c62b9975f4))

Bumps [beet](https://github.com/mcbeet/beet) from 0.67.0 to 0.67.1. - [Release
  notes](https://github.com/mcbeet/beet/releases) -
  [Changelog](https://github.com/mcbeet/beet/blob/main/CHANGELOG.md) -
  [Commits](https://github.com/mcbeet/beet/compare/v0.67.0...v0.67.1)

--- updated-dependencies: - dependency-name: beet dependency-type: direct:production

update-type: version-update:semver-patch ...

Signed-off-by: dependabot[bot] <support@github.com>

- **deps**: Bump mecha from 0.48.1 to 0.50.2
  ([`1cdf27b`](https://github.com/rx-modules/bolt-expressions/commit/1cdf27b807c797fd6edb38bc032b73dd67f8b4e5))

Bumps [mecha](https://github.com/mcbeet/mecha) from 0.48.1 to 0.50.2. - [Release
  notes](https://github.com/mcbeet/mecha/releases) -
  [Changelog](https://github.com/mcbeet/mecha/blob/main/CHANGELOG.md) -
  [Commits](https://github.com/mcbeet/mecha/compare/v0.48.1...v0.50.2)

--- updated-dependencies: - dependency-name: mecha dependency-type: direct:production

update-type: version-update:semver-minor ...

Signed-off-by: dependabot[bot] <support@github.com>

- **deps-dev**: Bump mudkip from 0.5.3 to 0.7.0
  ([`d9c1ab3`](https://github.com/rx-modules/bolt-expressions/commit/d9c1ab3f6f653f459a0d0f0bd0db2486a17a2ac3))

Bumps [mudkip](https://github.com/vberlier/mudkip) from 0.5.3 to 0.7.0. - [Release
  notes](https://github.com/vberlier/mudkip/releases) -
  [Changelog](https://github.com/vberlier/mudkip/blob/main/CHANGELOG.md) -
  [Commits](https://github.com/vberlier/mudkip/compare/v0.5.3...v0.7.0)

--- updated-dependencies: - dependency-name: mudkip dependency-type: direct:development

update-type: version-update:semver-minor ...

Signed-off-by: dependabot[bot] <support@github.com>

- **deps-dev**: Bump rich from 12.2.0 to 12.4.4
  ([`52b67d8`](https://github.com/rx-modules/bolt-expressions/commit/52b67d88b1f8c08d0c61c35498979d6c926ea185))

Bumps [rich](https://github.com/willmcgugan/rich) from 12.2.0 to 12.4.4. - [Release
  notes](https://github.com/willmcgugan/rich/releases) -
  [Changelog](https://github.com/Textualize/rich/blob/master/CHANGELOG.md) -
  [Commits](https://github.com/willmcgugan/rich/compare/v12.2.0...v12.4.4)

--- updated-dependencies: - dependency-name: rich dependency-type: direct:development

update-type: version-update:semver-minor ...

Signed-off-by: dependabot[bot] <support@github.com>

### Code Style

- Paint it black
  ([`04ba4b4`](https://github.com/rx-modules/bolt-expressions/commit/04ba4b44548b037a2822384cfc8453afedbf832a))

### Features

- Create multiple score sources at once
  ([`4eca574`](https://github.com/rx-modules/bolt-expressions/commit/4eca5743740799ec57def181559ff908d949e71c))

- Directly create score sources using the Scoreboard API
  ([`4d42c97`](https://github.com/rx-modules/bolt-expressions/commit/4d42c97990f872f107892cf6b2f27202343ceb28))

- Scale nbt data with multiplication/division
  ([`ebf9420`](https://github.com/rx-modules/bolt-expressions/commit/ebf942009d5696b57d695e05b3dfc2819f9029d3))

### Testing

- Update basic
  ([`7834ca7`](https://github.com/rx-modules/bolt-expressions/commit/7834ca7ee4e336e48a4bf34c804c28ec20b49c3e))

- Update snapshots
  ([`787c727`](https://github.com/rx-modules/bolt-expressions/commit/787c727548c35351fb4bf0623d99838470996184))


## v0.6.1 (2022-04-30)

### Bug Fixes

- Use `bolt` package instead of `mecha.contrib.bolt` in `api.py`
  ([`ace4b1a`](https://github.com/rx-modules/bolt-expressions/commit/ace4b1ae5f637f771e819e6bb83a32cd8a92866b))

### Chores

- Add bolt package and update mecha
  ([`bfbd870`](https://github.com/rx-modules/bolt-expressions/commit/bfbd8706d4c2a6332bcbb680dedced0e053296e9))

- Update `bolt`
  ([`8e614d9`](https://github.com/rx-modules/bolt-expressions/commit/8e614d90614a7fa56f01c7e97e2405242b4016ef))

- Use custom fork of pygments ([#10](https://github.com/rx-modules/bolt-expressions/pull/10),
  [`3f1c6a0`](https://github.com/rx-modules/bolt-expressions/commit/3f1c6a096d62ab5fce5803f4d78c1a32d66ed97f))

Now using https://github.com/rx-modules/pygments for pygments which adds a `mcfunction` parser.
  Also, added `CACHE_SECRET` to `.github/workflows/main.yml` action to allow us to refresh the cache
  when needed. Co-authored-by: rx97 <rx97>

- **deps**: Bump beet from 0.55.0 to 0.56.0
  ([`5003265`](https://github.com/rx-modules/bolt-expressions/commit/50032656ad82631b47151f0ceecce82430799cc2))

Bumps [beet](https://github.com/mcbeet/beet) from 0.55.0 to 0.56.0. - [Release
  notes](https://github.com/mcbeet/beet/releases) -
  [Changelog](https://github.com/mcbeet/beet/blob/main/CHANGELOG.md) -
  [Commits](https://github.com/mcbeet/beet/compare/v0.55.0...v0.56.0)

--- updated-dependencies: - dependency-name: beet dependency-type: direct:production

update-type: version-update:semver-minor ...

Signed-off-by: dependabot[bot] <support@github.com>

- **deps**: Bump mecha from 0.43.1 to 0.43.3
  ([`72b2eba`](https://github.com/rx-modules/bolt-expressions/commit/72b2eba446079d088507e3d706ad925424d804ef))

Bumps [mecha](https://github.com/mcbeet/mecha) from 0.43.1 to 0.43.3. - [Release
  notes](https://github.com/mcbeet/mecha/releases) -
  [Changelog](https://github.com/mcbeet/mecha/blob/main/CHANGELOG.md) -
  [Commits](https://github.com/mcbeet/mecha/compare/v0.43.1...v0.43.3)

--- updated-dependencies: - dependency-name: mecha dependency-type: direct:production

update-type: version-update:semver-patch ...

Signed-off-by: dependabot[bot] <support@github.com>

- **deps-dev**: Bump mudkip from 0.5.1 to 0.5.3
  ([`b23fd1e`](https://github.com/rx-modules/bolt-expressions/commit/b23fd1ede2ca9cb06f04d9303792a9aae5481f33))

Bumps [mudkip](https://github.com/vberlier/mudkip) from 0.5.1 to 0.5.3. - [Release
  notes](https://github.com/vberlier/mudkip/releases) -
  [Changelog](https://github.com/vberlier/mudkip/blob/main/CHANGELOG.md) -
  [Commits](https://github.com/vberlier/mudkip/compare/v0.5.1...v0.5.3)

--- updated-dependencies: - dependency-name: mudkip dependency-type: direct:development

update-type: version-update:semver-patch ...

Signed-off-by: dependabot[bot] <support@github.com>

- **deps-dev**: Bump rich from 12.0.1 to 12.2.0
  ([`03926b7`](https://github.com/rx-modules/bolt-expressions/commit/03926b7409e00e9cb4c70c3085b9faceaa820ceb))

Bumps [rich](https://github.com/willmcgugan/rich) from 12.0.1 to 12.2.0. - [Release
  notes](https://github.com/willmcgugan/rich/releases) -
  [Changelog](https://github.com/Textualize/rich/blob/master/CHANGELOG.md) -
  [Commits](https://github.com/willmcgugan/rich/compare/v12.0.1...v12.2.0)

--- updated-dependencies: - dependency-name: rich dependency-type: direct:development

update-type: version-update:semver-minor ...

Signed-off-by: dependabot[bot] <support@github.com>

### Code Style

- Paint it black
  ([`606efaa`](https://github.com/rx-modules/bolt-expressions/commit/606efaa56ef9d1ee72b72787bf2f6a5434febfaa))

### Documentation

- Changes related to the new `bolt` package.
  ([`6ceac3b`](https://github.com/rx-modules/bolt-expressions/commit/6ceac3bc93a4e6949302eb96bb68ef60d8c2461b))

- Fix tutorial codeblocks not using mcfunction lang
  ([`aff3d90`](https://github.com/rx-modules/bolt-expressions/commit/aff3d905f87ccdd8a74467a38d8f925f550780af))

### Testing

- Update `mecha.contrib.bolt` to `bolt`
  ([`9b688c2`](https://github.com/rx-modules/bolt-expressions/commit/9b688c2cd64e7ad9819edaa4d73cfd205480828f))


## v0.6.0 (2022-04-14)

### Chores

- **deps-dev**: Bump black from 22.1.0 to 22.3.0
  ([`7658d11`](https://github.com/rx-modules/bolt-expressions/commit/7658d1132a5a8c23d5efe246406f2d695ec3777f))

Bumps [black](https://github.com/psf/black) from 22.1.0 to 22.3.0. - [Release
  notes](https://github.com/psf/black/releases) -
  [Changelog](https://github.com/psf/black/blob/main/CHANGES.md) -
  [Commits](https://github.com/psf/black/compare/22.1.0...22.3.0)

--- updated-dependencies: - dependency-name: black dependency-type: direct:development

update-type: version-update:semver-minor ...

Signed-off-by: dependabot[bot] <support@github.com>

### Features

- Add expression node methods
  ([`97b5a44`](https://github.com/rx-modules/bolt-expressions/commit/97b5a44253370aeaef5d9c820e4ef93c4f4950c9))


## v0.5.0 (2022-04-02)

### Documentation

- Add generated commands to `tutorial.md`
  ([`8711845`](https://github.com/rx-modules/bolt-expressions/commit/8711845d32176c43224f3ed1e169e7380e413bcf))

- Fix docs for now
  ([`8a0f02a`](https://github.com/rx-modules/bolt-expressions/commit/8a0f02adbd6028ae13f5f146c80a3ae326a9c36e))

### Features

- `holder` and `obj` property aliases for score sources.
  ([`e6bfdb8`](https://github.com/rx-modules/bolt-expressions/commit/e6bfdb8b5cc3919104a1ef532a2365df4324ca84))

``` temp = Scoreboard("abc.temp") value = temp["@a[tag=abc.selected]"]

value.scoreholder # @a[tag=abc.selected] value.objective # abc.temp

value.holder # @a[tag=abc.selected] value.obj # abc.temp ```

- `objective_prefix` config, optional `prefixed` flag when creating an objective.
  ([`6c43d51`](https://github.com/rx-modules/bolt-expressions/commit/6c43d51dd78b0c0da5cb239766bbeabd4359b84f))

``` meta: bolt_expressions: objective_prefix: abc.foo. ``` ``` temp = Scoreboard.objective("temp") #
  abc.foo.temp

test = Scoreboard.objective("testing.obj", prefixed=False) # testing.obj ```

### Refactoring

- Let `Operation.unroll` reuse temp scores, remove `temp_var_collapsing` rule.
  ([`7b50867`](https://github.com/rx-modules/bolt-expressions/commit/7b50867737ecc6e31b23a583cea5cdd537a804fb))

### Testing

- Update `operation_basics`
  ([`556a956`](https://github.com/rx-modules/bolt-expressions/commit/556a956eb0b463bc1f1acf619895e33433aeba79))

- Update snapshots, temp scores changed again.
  ([`8bfa7f3`](https://github.com/rx-modules/bolt-expressions/commit/8bfa7f307401495e33d640e4f8ff9cf874200ca6))


## v0.4.5 (2022-03-31)

### Bug Fixes

- Init function would be prepended to load tag even if `Expression.init` was called
  ([`34080fe`](https://github.com/rx-modules/bolt-expressions/commit/34080fe170b2a43148917d635f95602a9f52e57e))

### Code Style

- Paint it black
  ([`b4712de`](https://github.com/rx-modules/bolt-expressions/commit/b4712decb8c166217a6d9d04331477d3768fea2e))

### Documentation

- Adjust tutorial
  ([`4077a70`](https://github.com/rx-modules/bolt-expressions/commit/4077a7059393771318431b20ea1810846f05543d))

- Fix table of contents
  ([`2fb5935`](https://github.com/rx-modules/bolt-expressions/commit/2fb5935c4a8cf48bbe89947c6a147a4414bea70d))

### Testing

- Init function and `Expression.init`
  ([`70b2381`](https://github.com/rx-modules/bolt-expressions/commit/70b23815fc42390657bea1cbcd0202c7e4d36854))

- Renamed `combo_init_function_call`
  ([`abe5ad5`](https://github.com/rx-modules/bolt-expressions/commit/abe5ad5e95d0d700e700fba4c11b98233c331f59))


## v0.4.4 (2022-03-31)


## v0.4.3 (2022-03-31)

### Bug Fixes

- Expression.init() creates function with incorrect init path
  ([`665edcc`](https://github.com/rx-modules/bolt-expressions/commit/665edccefb89b669cb72a5d6e1d27dcdfd990380))

- Generate_init error
  ([`65f8b5a`](https://github.com/rx-modules/bolt-expressions/commit/65f8b5aa67f75fb1eeb5674e68c9a9f42a4e9215))


## v0.4.2 (2022-03-31)

### Bug Fixes

- Forcing a release to build new docs ffs
  ([`e30adf7`](https://github.com/rx-modules/bolt-expressions/commit/e30adf7d2ddd2137a5e13921e5a405046b94ee09))

### Chores

- .gitignore
  ([`c19be44`](https://github.com/rx-modules/bolt-expressions/commit/c19be44d8aea6e28eb1a2e16642dacfc55b47ebb))

### Documentation

- Auto build and deploy docs
  ([`3f8bf8e`](https://github.com/rx-modules/bolt-expressions/commit/3f8bf8e6602d4b584a28ef1832f102f50babed2b))

- Fix workflow (3.10 versus "3.10")
  ([`9cbc582`](https://github.com/rx-modules/bolt-expressions/commit/9cbc582b463c352fb0a5c34662205c2e6fdf8220))

- Old usage on README.md fixed
  ([`60808b1`](https://github.com/rx-modules/bolt-expressions/commit/60808b1b41bb3dba5bb70afdc4c59eec0c3fbcfc))


## v0.4.1 (2022-03-31)

### Bug Fixes

- Scoreboard.objective now works and is preferred
  ([`e292d99`](https://github.com/rx-modules/bolt-expressions/commit/e292d994a3e7e913655ed31610693deeabc434a5))

### Documentation

- Added tutorial and cleaned README.md
  ([`b786052`](https://github.com/rx-modules/bolt-expressions/commit/b78605200aff225dc838b82141dd466cf3f82904))


## v0.4.0 (2022-03-31)

### Code Style

- Paint it black
  ([`5b2d976`](https://github.com/rx-modules/bolt-expressions/commit/5b2d9767a43f6aea1f7336ccee9debc168f58e98))


## v0.3.0 (2022-03-31)

### Bug Fixes

- Rmin and rmax now function correctly
  ([`3410fee`](https://github.com/rx-modules/bolt-expressions/commit/3410fee31a0aab0a02bce37a09141682c8a847d3))

- Tests now properly index ensuring that github passes all tests
  ([`77aafd1`](https://github.com/rx-modules/bolt-expressions/commit/77aafd18dc6e633a0ac62b0363413eb1c5ac8046))

### Chores

- Random vscode settings
  ([`13004c1`](https://github.com/rx-modules/bolt-expressions/commit/13004c1048351893a7ec44b0e064e01f0b81fa20))

### Code Style

- Adjusted comments
  ([`3b3d725`](https://github.com/rx-modules/bolt-expressions/commit/3b3d725c48b61728a4b4794b2f4fe7d47bd146a2))

- Removed #fmt: skip
  ([`86fed67`](https://github.com/rx-modules/bolt-expressions/commit/86fed674b6f4fdda580775cee1499d0e2c54b64d))

- Rename bolt_expressions to make ./plugin less busy
  ([`bffd733`](https://github.com/rx-modules/bolt-expressions/commit/bffd733fa881914cb8069b616fd6ee689314ca73))

### Features

- Ctx.inject is now implicit
  ([`f29406f`](https://github.com/rx-modules/bolt-expressions/commit/f29406f3672b6a47779faf7a3ef2767dfa2d5402))

```py from bolt_expressions import Scoreboard, Data

abc = Scoreboard("abc.main") abc["@s"] += 10 ```

- New NBT DataSource feature
  ([`9660bbb`](https://github.com/rx-modules/bolt-expressions/commit/9660bbb96766f1df0464c1ed5d2b50360076e01e))

new: `from bolt_expressions import Data` allows you to manipulate data storage, entity, and blocks

fix: smoother library operations (hopefully)

- Objectives and constants now properly init on load
  ([`9838212`](https://github.com/rx-modules/bolt-expressions/commit/98382122af225bac71af3ec861663d751b9ef914))

new: `init_path` option now holds init'd objectives and constants automatically prepended to
  `#minecraft:load` unless manually invoked

### Testing

- Fix namespaces
  ([`e159270`](https://github.com/rx-modules/bolt-expressions/commit/e159270257416225c36c77377b7d2ee18584480c))

- New test cases, operation_complex, combo_smithed, operation_basics
  ([`a408574`](https://github.com/rx-modules/bolt-expressions/commit/a408574db9f1740e7b03b0b710b58fccb8108534))


## v0.2.1 (2022-03-28)

### Bug Fixes

- __min__ and __max__ now functions without ducking
  ([`777f71b`](https://github.com/rx-modules/bolt-expressions/commit/777f71b02da5744c7c5534e67b763c7ea3a21247))

- Missing callback reference
  ([`084a0f5`](https://github.com/rx-modules/bolt-expressions/commit/084a0f5d9a6a9745e444271af200dfb3f8bc98fd))

- More missing callbacks
  ([`c6451e8`](https://github.com/rx-modules/bolt-expressions/commit/c6451e8c59f751517647c8a3304f4e3c5ac7bda2))

### Code Style

- Paint it black
  ([`5228820`](https://github.com/rx-modules/bolt-expressions/commit/52288203238b826f9367ea7345e71ac185f291a7))

### Refactoring

- Expression API
  ([`e75f157`](https://github.com/rx-modules/bolt-expressions/commit/e75f157c6461f69951ccb77798d2643e7411dfc8))

refactor: use proper option validation

fix: readded min and max

### Testing

- Renamed example tests
  ([`c32335f`](https://github.com/rx-modules/bolt-expressions/commit/c32335fc2471122aa1b2b383295adfb60b7da6a4))


## v0.2.0 (2022-03-28)

### Bug Fixes

- Fix github workflows
  ([`c65c1af`](https://github.com/rx-modules/bolt-expressions/commit/c65c1af517a25581e6a03931df4e9530ad9ac3ce))

- Make less temp vars
  ([`043605f`](https://github.com/rx-modules/bolt-expressions/commit/043605fb5af268c46c5b34917d2b673972be12f7))

- Pyproject.toml version var mismatch
  ([`1ce816d`](https://github.com/rx-modules/bolt-expressions/commit/1ce816ddcf228d06283468915b4ce7fa20cd112c))

### Chores

- Fix badges
  ([`486b85f`](https://github.com/rx-modules/bolt-expressions/commit/486b85f4304abf8148cce7d2161c2c3087e79dac))

- Remove rich, accidental import
  ([`31d5d59`](https://github.com/rx-modules/bolt-expressions/commit/31d5d596304d6e2238e76b6c1aa92c9a0758a628))

- Update deps
  ([`2a542e5`](https://github.com/rx-modules/bolt-expressions/commit/2a542e5b933249041eb3de29a97226237be3d456))

- Update deps
  ([`3997dfe`](https://github.com/rx-modules/bolt-expressions/commit/3997dfe6ac25ef6725cab3fe5941483fc60cffff))

### Code Style

- Formattting
  ([`4753322`](https://github.com/rx-modules/bolt-expressions/commit/475332296694c823fead7fd7ecdc8480a40881c1))

- Losely -> loosely
  ([`7e49f07`](https://github.com/rx-modules/bolt-expressions/commit/7e49f0708f9cba0001008cf65e7144d1c85934e6))

- Minor renames
  ([`4a47be5`](https://github.com/rx-modules/bolt-expressions/commit/4a47be53fda3232e06690fe0e09581338ea81896))

### Features

- Added __min__ and __max__ functionality (ducked currently)
  ([`d359ade`](https://github.com/rx-modules/bolt-expressions/commit/d359ade7ee21662e259979635928187920933f6c))

- Paint it black: 0.2.0
  ([`4abaf39`](https://github.com/rx-modules/bolt-expressions/commit/4abaf3993a70377c23f8073a7b544a929ebbceb3))

- Smartgenerator
  ([`f1d0bab`](https://github.com/rx-modules/bolt-expressions/commit/f1d0bab5d7b4b906c1eca3b1e5c3bfdb358955b4))

### Refactoring

- Major restructure with multiple files.
  ([`02cf5de`](https://github.com/rx-modules/bolt-expressions/commit/02cf5de5ab07fe8382b132716f6324209a7c413b))

feat: - decorator to add new magic methods - node behavior split into many files - avoids circular
  imports

Co-authored-by: TheWii <TheWii@users.noreply.github.com>

- Repo restructure
  ([`4538e5d`](https://github.com/rx-modules/bolt-expressions/commit/4538e5ddcec0864373205df25029f7153685bb2b))

### Testing

- Ignore type checking for now
  ([`2fcaf78`](https://github.com/rx-modules/bolt-expressions/commit/2fcaf786f418e6f5a609c2963bb8e6d3dbabe829))

- Introduced pytest-insta reviewing
  ([`8fffd7b`](https://github.com/rx-modules/bolt-expressions/commit/8fffd7bbfb0917db09e12104797bc0ee3a0a1e5e))

- Load_minmax
  ([`56f16f1`](https://github.com/rx-modules/bolt-expressions/commit/56f16f114d0cc4858063380b120ca166b5941fab))

- Remove doctest
  ([`39b635a`](https://github.com/rx-modules/bolt-expressions/commit/39b635a0decc2975d71d27f83ce0cdc2f86000f2))

- Remove lectern tests
  ([`bc19b34`](https://github.com/rx-modules/bolt-expressions/commit/bc19b340824a87d086889bbcfddfef57cd2fc754))
