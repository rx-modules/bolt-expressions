# Changelog

<!--next-version-placeholder-->

## v0.12.1 (2022-12-31)
### Fix
* Preserve key/default logic of builtin min/max functions ([`c127114`](https://github.com/rx-modules/bolt-expressions/commit/c127114beefff5e392cc3e4733b7c113202ccf91))

## v0.12.0 (2022-12-30)
### Feature
* Support literal floating numbers on score multiplication/division ([`eea20d4`](https://github.com/rx-modules/bolt-expressions/commit/eea20d4d6a587e278f0a8bf8a7cae3a431b00fdd))

### Fix
* Make wrapped min/max functions behave more like the builtin ones ([`7e3b400`](https://github.com/rx-modules/bolt-expressions/commit/7e3b4003e677bf7a1bd9c4728f332f63e6a12081))
* Remove commands that multiply/divide by 1, add/subtract by 0 ([`6d8cf88`](https://github.com/rx-modules/bolt-expressions/commit/6d8cf882b029d49b120116ed088ee395d3902132))

## v0.11.2 (2022-12-27)
### Fix
* Import all subpackages in __init__ for conveniency ([`7c2ed2c`](https://github.com/rx-modules/bolt-expressions/commit/7c2ed2c65d80b1e0f91efd970724414c24fd3e91))

## v0.11.1 (2022-12-27)
### Fix
* Generate negative score constants in init function ([`9ec47cb`](https://github.com/rx-modules/bolt-expressions/commit/9ec47cb3b7aa4e1d0baf865a2fa29a902eae1790))

## v0.11.0 (2022-11-19)
### Feature
* Implicitly convert sources into text components ([`d27870e`](https://github.com/rx-modules/bolt-expressions/commit/d27870ef068b27dddf054b01d6c418d608a0a61a))
* Add `component` method to convert sources into text components ([`a22caf9`](https://github.com/rx-modules/bolt-expressions/commit/a22caf9256c234944ff1de41829d48e7c37ddc9b))

## v0.10.0 (2022-11-15)
### Feature
* Require bolt_expressions.contrib.commands by default ([`f748ee3`](https://github.com/rx-modules/bolt-expressions/commit/f748ee3ea2e6cc5eb9416d295ce39001d03856da))
* Add bolt_expressions.contrib.commands ([`e40ae95`](https://github.com/rx-modules/bolt-expressions/commit/e40ae9562bae5589a0c541a60884ce79211febf8))

## v0.9.0 (2022-11-07)
### Feature
* Let custom objectives be added to init function ([`99483fb`](https://github.com/rx-modules/bolt-expressions/commit/99483fbbcd4c3653b40cc3eed0c948843699caea))

## v0.8.3 (2022-11-07)
### Fix
* Generate init function only when needed ([`01f3193`](https://github.com/rx-modules/bolt-expressions/commit/01f3193d56d79c62608ff239b8f26032c1cc2685))
* Prevent init function from having unused objectives ([`4b6a490`](https://github.com/rx-modules/bolt-expressions/commit/4b6a490b47345e5ee66e386c839aebc052c22ac4))
* Prevent init function from having duplicated/unused constants ([`05a2638`](https://github.com/rx-modules/bolt-expressions/commit/05a2638a8e9f637f443b2a98419544b3abd75127))

## v0.8.2 (2022-08-28)
### Fix
* DataSource._copy doesn't support subclasses. ([`21d1db3`](https://github.com/rx-modules/bolt-expressions/commit/21d1db3447061fa5eefcaf60aae8ac9b755e4d5e))

## v0.8.1 (2022-08-24)
### Fix
* Let dicts be used as filter keys in DataSource paths ([`f10cbdf`](https://github.com/rx-modules/bolt-expressions/commit/f10cbdfdc334b67d1303f920d9512271ced2a540))

## v0.8.0 (2022-07-27)
### Feature
* Api method to cast expressions to any nbt type ([`eb3d532`](https://github.com/rx-modules/bolt-expressions/commit/eb3d53227df26d48f8291f1f0137ccc12f75caba))

### Fix
* Better nbt type handling ([`9f63995`](https://github.com/rx-modules/bolt-expressions/commit/9f63995b4fdfd38803da54260acd18bb09493c45))
* Scaling/casting between data sources doesn't work ([`5074414`](https://github.com/rx-modules/bolt-expressions/commit/50744149cf3a16cefce18e42d096ffc44196f1bc))

## v0.7.0 (2022-06-15)
### Feature
* Scale nbt data with multiplication/division ([`ebf9420`](https://github.com/rx-modules/bolt-expressions/commit/ebf942009d5696b57d695e05b3dfc2819f9029d3))
* Directly create score sources using the Scoreboard API ([`4d42c97`](https://github.com/rx-modules/bolt-expressions/commit/4d42c97990f872f107892cf6b2f27202343ceb28))
* Create multiple score sources at once ([`4eca574`](https://github.com/rx-modules/bolt-expressions/commit/4eca5743740799ec57def181559ff908d949e71c))

## v0.6.1 (2022-04-30)
### Fix
* Use `bolt` package instead of `mecha.contrib.bolt` in `api.py` ([`ace4b1a`](https://github.com/rx-modules/bolt-expressions/commit/ace4b1ae5f637f771e819e6bb83a32cd8a92866b))

### Documentation
* Changes related to the new `bolt` package. ([`6ceac3b`](https://github.com/rx-modules/bolt-expressions/commit/6ceac3bc93a4e6949302eb96bb68ef60d8c2461b))
* Fix tutorial codeblocks not using mcfunction lang ([`aff3d90`](https://github.com/rx-modules/bolt-expressions/commit/aff3d905f87ccdd8a74467a38d8f925f550780af))

## v0.6.0 (2022-04-14)
### Feature
* Add expression node methods ([`97b5a44`](https://github.com/rx-modules/bolt-expressions/commit/97b5a44253370aeaef5d9c820e4ef93c4f4950c9))

## v0.5.0 (2022-04-02)
### Feature
* `objective_prefix` config, optional `prefixed` flag when creating an objective. ([`6c43d51`](https://github.com/rx-modules/bolt-expressions/commit/6c43d51dd78b0c0da5cb239766bbeabd4359b84f))
* `holder` and `obj` property aliases for score sources. ([`e6bfdb8`](https://github.com/rx-modules/bolt-expressions/commit/e6bfdb8b5cc3919104a1ef532a2365df4324ca84))

### Documentation
* Fix docs for now ([`8a0f02a`](https://github.com/rx-modules/bolt-expressions/commit/8a0f02adbd6028ae13f5f146c80a3ae326a9c36e))
* Add generated commands to `tutorial.md` ([`8711845`](https://github.com/rx-modules/bolt-expressions/commit/8711845d32176c43224f3ed1e169e7380e413bcf))

## v0.4.5 (2022-03-31)
### Fix
* Init function would be prepended to load tag even if `Expression.init` was called ([`34080fe`](https://github.com/rx-modules/bolt-expressions/commit/34080fe170b2a43148917d635f95602a9f52e57e))

### Documentation
* Adjust tutorial ([`4077a70`](https://github.com/rx-modules/bolt-expressions/commit/4077a7059393771318431b20ea1810846f05543d))
* Fix table of contents ([`2fb5935`](https://github.com/rx-modules/bolt-expressions/commit/2fb5935c4a8cf48bbe89947c6a147a4414bea70d))

## v0.4.4 (2022-03-31)
### Fix
* Expression.init() creates function with incorrect init path ([`665edcc`](https://github.com/rx-modules/bolt-expressions/commit/665edccefb89b669cb72a5d6e1d27dcdfd990380))

## v0.4.3 (2022-03-31)
### Fix
* Generate_init error ([`65f8b5a`](https://github.com/rx-modules/bolt-expressions/commit/65f8b5aa67f75fb1eeb5674e68c9a9f42a4e9215))

## v0.4.2 (2022-03-31)
### Fix
* Forcing a release to build new docs ffs ([`e30adf7`](https://github.com/rx-modules/bolt-expressions/commit/e30adf7d2ddd2137a5e13921e5a405046b94ee09))

### Documentation
* Fix workflow (3.10 versus "3.10") ([`9cbc582`](https://github.com/rx-modules/bolt-expressions/commit/9cbc582b463c352fb0a5c34662205c2e6fdf8220))
* Auto build and deploy docs ([`3f8bf8e`](https://github.com/rx-modules/bolt-expressions/commit/3f8bf8e6602d4b584a28ef1832f102f50babed2b))
* Old usage on README.md fixed ([`60808b1`](https://github.com/rx-modules/bolt-expressions/commit/60808b1b41bb3dba5bb70afdc4c59eec0c3fbcfc))
* Added tutorial and cleaned README.md ([`b786052`](https://github.com/rx-modules/bolt-expressions/commit/b78605200aff225dc838b82141dd466cf3f82904))

## v0.4.1 (2022-03-31)
### Fix
* Scoreboard.objective now works and is preferred ([`e292d99`](https://github.com/rx-modules/bolt-expressions/commit/e292d994a3e7e913655ed31610693deeabc434a5))

## v0.4.0 (2022-03-31)
### Feature
* Ctx.inject is now implicit ([`f29406f`](https://github.com/rx-modules/bolt-expressions/commit/f29406f3672b6a47779faf7a3ef2767dfa2d5402))

## v0.3.0 (2022-03-31)
### Feature
* New NBT DataSource feature ([`9660bbb`](https://github.com/rx-modules/bolt-expressions/commit/9660bbb96766f1df0464c1ed5d2b50360076e01e))
* Objectives and constants now properly init on load ([`9838212`](https://github.com/rx-modules/bolt-expressions/commit/98382122af225bac71af3ec861663d751b9ef914))

### Fix
* Tests now properly index ensuring that github passes all tests ([`77aafd1`](https://github.com/rx-modules/bolt-expressions/commit/77aafd18dc6e633a0ac62b0363413eb1c5ac8046))
* Rmin and rmax now function correctly ([`3410fee`](https://github.com/rx-modules/bolt-expressions/commit/3410fee31a0aab0a02bce37a09141682c8a847d3))
* More missing callbacks ([`c6451e8`](https://github.com/rx-modules/bolt-expressions/commit/c6451e8c59f751517647c8a3304f4e3c5ac7bda2))

## v0.2.1 (2022-03-28)
### Fix
* Missing callback reference ([`084a0f5`](https://github.com/rx-modules/bolt-expressions/commit/084a0f5d9a6a9745e444271af200dfb3f8bc98fd))
* __min__ and __max__ now functions without ducking ([`777f71b`](https://github.com/rx-modules/bolt-expressions/commit/777f71b02da5744c7c5534e67b763c7ea3a21247))

## v0.2.0 (2022-03-28)
### Feature
* Paint it black: 0.2.0 ([`4abaf39`](https://github.com/rx-modules/bolt-expressions/commit/4abaf3993a70377c23f8073a7b544a929ebbceb3))
* Added __min__ and __max__ functionality (ducked currently) ([`d359ade`](https://github.com/rx-modules/bolt-expressions/commit/d359ade7ee21662e259979635928187920933f6c))
* SmartGenerator ([`f1d0bab`](https://github.com/rx-modules/bolt-expressions/commit/f1d0bab5d7b4b906c1eca3b1e5c3bfdb358955b4))

### Fix
* Pyproject.toml version var mismatch ([`1ce816d`](https://github.com/rx-modules/bolt-expressions/commit/1ce816ddcf228d06283468915b4ce7fa20cd112c))
* Fix github workflows ([`c65c1af`](https://github.com/rx-modules/bolt-expressions/commit/c65c1af517a25581e6a03931df4e9530ad9ac3ce))
* Make less temp vars ([`043605f`](https://github.com/rx-modules/bolt-expressions/commit/043605fb5af268c46c5b34917d2b673972be12f7))
