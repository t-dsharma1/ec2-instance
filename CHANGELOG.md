# Changelog

## [1.21.0](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/compare/v1.20.0...v1.21.0) (2025-01-10)


### Features

* Added archival process to archive older conversations to seperate table ([#147](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/issues/147)) ([4cd0501](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/4cd0501702fa8a92b162f450c06765b4611943c6))* break retrievers dependency ([#148](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/issues/148)) ([88cd2c8](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/88cd2c866543e470509d463d2a800910f1845081))

## [1.20.0](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/compare/v1.19.3...v1.20.0) (2024-11-27)


### Features

* Add ambience noise level configuration to FlowVoiceConfig. ([#145](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/issues/145)) ([32b9320](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/32b9320a9fef31162cbcf6148262e6bab25c0905))

## [1.19.3](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/compare/v1.19.2...v1.19.3) (2024-11-20)


### Bug Fixes

* Updated max_conversation history in base_config for seeds ([#143](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/issues/143)) ([065535c](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/065535c1c83914e6bfee8d46df4c33cc3921eb64))

## [1.19.2](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/compare/v1.19.1...v1.19.2) (2024-10-30)


### Bug Fixes

* Add missing languages to Azure TTS ([#141](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/issues/141)) ([e9c8437](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/e9c8437aa5b50207fc4ae4fd4cd2b30111ed8331))

## [1.19.1](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/compare/v1.19.0...v1.19.1) (2024-10-28)


### Bug Fixes

* Add prometheus metric for llm prompt length ([#139](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/issues/139)) ([1cb1f2e](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/1cb1f2ed9a7e847748c60311d2777a70b1a774a5))

## [1.19.0](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/compare/v1.18.1...v1.19.0) (2024-10-18)


### Features

* Azure STT and TTS ([#135](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/issues/135)) ([8ecbbf3](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/8ecbbf33069a0fe2bdc3ec3df4169a314f8e818c))

### Bug Fixes

* Do not create new conversation if conversation_pk is passed in input message ([#136](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/issues/136)) ([88836b0](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/88836b0e4cc31226b1d72e49855d22203b0334c1))

## [1.18.1](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/compare/v1.18.0...v1.18.1) (2024-10-17)


### Bug Fixes

* Make Amazon Transcribe a default STT platform ([#133](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/issues/133)) ([227a771](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/227a7718e840a1d30bd57e7ae3de83175f909628))

## [1.18.0](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/compare/v1.17.0...v1.18.0) (2024-10-16)


### Features

* Add language code and validation for stability and similarity boost parameters in FlowVoiceConfigElevenlabsParams ([#131](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/issues/131)) ([6c1a5d1](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/6c1a5d1f638fac3a85b3afd2b5fff922abfcc5af))

## [1.17.0](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/compare/v1.16.0...v1.17.0) (2024-10-16)


### Features

* Add stability and similarity boost parameters to FlowVoiceConfigElevenlabsParams ([#127](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/issues/127)) ([5d58e95](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/5d58e954a03f6c01480f3de8171f24f5ae30845e))

## [1.16.0](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/compare/v1.15.2...v1.16.0) (2024-10-15)


### Features

* break retrievers dependency ([#128](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/issues/128)) ([b1bef88](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/b1bef883411f5ad6fc866c5d8fe531c5b95a6a34))

## [1.15.2](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/compare/v1.15.1...v1.15.2) (2024-10-11)


### Bug Fixes

* Send full static message as LLM response, even while streaming. ([#125](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/issues/125)) ([b88422e](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/b88422eb1b948341a922ca2d7a9b346c6eb013ba))

## [1.15.1](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/compare/v1.15.0...v1.15.1) (2024-10-10)


### Bug Fixes

* Add app name prefix to all promethes metrics ([ea8bd69](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/ea8bd69eba598b204b368c870a00feb07d3530d8))* Add app name prefix to all prometheus metrics ([#123](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/issues/123)) ([ea8bd69](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/ea8bd69eba598b204b368c870a00feb07d3530d8))* Fix proper aws transcribe language codes ([#122](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/issues/122)) ([d029fba](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/d029fbac36ea088aeae21d82d828ff35116b4953))

## [1.15.0](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/compare/v1.14.2...v1.15.0) (2024-10-02)


### Features

* Add Cartesia platform to flow type ([#119](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/issues/119)) ([2357ec9](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/2357ec940ae8ff2e9729b2258280df02194cc9f9))

### Bug Fixes

* wrong Cartesia model ([#121](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/issues/121)) ([13baeb0](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/13baeb0a579740109ecdbd08ccb389809d57e785))

## [1.14.2](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/compare/v1.14.1...v1.14.2) (2024-09-24)


### Bug Fixes

* Add debug logs to query dynamodb method ([#115](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/issues/115)) ([4a5277c](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/4a5277c61b2a44d580c14afcfa040457dae71fc7))* Use db init aws key for tests ([#114](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/issues/114)) ([2f7d550](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/2f7d5503343c21d01d9fdb5e13077faac9d2b5fd))

## [1.14.1](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/compare/v1.14.0...v1.14.1) (2024-09-24)


### Bug Fixes

* Use a custom unpickler to handle old compressed flows without error ([#112](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/issues/112)) ([d49008f](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/d49008f19f9d7e7028a5a7cd039b52bf4e1949b1))

## [1.14.0](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/compare/v1.13.0...v1.14.0) (2024-09-23)


### Features

* Add voice_config to Flow object ([#110](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/issues/110)) ([88684ba](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/88684ba387aa6e66e9e8e7096486035167e5fc2f))

## [1.13.0](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/compare/v1.12.0...v1.13.0) (2024-09-23)


### Features

* Introduce poetry to manage dependencies with proper locking and extract a genie_dao and genie_core packages ([#108](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/issues/108)) ([d2ef2b9](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/d2ef2b9327186dd8329c96f87e37b5ab561818ad))

## [1.12.0](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/compare/v1.11.2...v1.12.0) (2024-09-05)


### Features

* add customer context field ([#106](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/issues/106)) ([ccd397b](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/ccd397b02e8a90f953bc0b749f889f5cc087edcb))

## [1.11.2](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/compare/v1.11.1...v1.11.2) (2024-09-03)


### Bug Fixes

* Use create_task instead of run_until_complete when sending messages through WS ([#103](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/issues/103)) ([0b04f25](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/0b04f25a608418079c61b39f25da20b581349bd5))

## [1.11.1](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/compare/v1.11.0...v1.11.1) (2024-09-03)


### Bug Fixes

* Use sync listeners in aiopubsub to make sure all LLM chunks are dispatched immediately ([#101](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/issues/101)) ([4482518](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/4482518a2c149e5bee8fd85a92a779f6cc0b9961))

## [1.11.0](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/compare/v1.10.1...v1.11.0) (2024-09-02)


### Features

* Make agent ws API request-response instead of forever running loop ([#99](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/issues/99)) ([55a717e](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/55a717e27333ba2b3293ccc87baa293c1e226409))

## [1.10.1](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/compare/v1.10.0...v1.10.1) (2024-09-02)


### Bug Fixes

* Remove double call of handle_conversation_call ([#97](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/issues/97)) ([f3222c1](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/f3222c19798847190232c4e7c8199995925d5cc0))

## [1.10.0](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/compare/v1.9.0...v1.10.0) (2024-09-02)


### Features

* add external_data field and incorporate fields into context ([#86](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/issues/86)) ([27fd336](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/27fd336b0c147092900d3a40ee2c0dc0d91dee3d))* Add response_completed attribute to agent response object and add rollback on message logic ([#94](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/issues/94)) ([9ab08bf](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/9ab08bfe74f7d2680ea71c26887c2bfaac508165))

## [1.9.0](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/compare/v1.8.0...v1.9.0) (2024-08-22)


### Features

* Send callsight response in ably message data field ([#88](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/issues/88)) ([0b943ca](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/0b943ca7d1c26e123ecd10c87cc1a4bcf5496420))

### Bug Fixes

* Updated github workflow for callsight url of diff envs ([#87](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/issues/87)) ([3372d21](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/3372d21cfab0e22dc16d4b357745879caece1650))

## [1.8.0](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/compare/v1.7.0...v1.8.0) (2024-08-14)


### Features

* Add option for entrypoint to rollback or manually commit db batch of handle_conversation_flow ([#81](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/issues/81)) ([4b00fc8](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/4b00fc8fe3007651d5a275ecffb2f745d2606e0b))

### Bug Fixes

* update callsight default config ([c4118d4](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/c4118d4d4685b77a1274c04e90a7fc0400c7a01b))* update flow version number and callsight params ([0ac5f6f](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/0ac5f6fe7c0972e7030a3730030fee1e3d52ef15))* update flow version number and callsight params ([a0f6613](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/a0f6613dd02b7b40aaa1623ce6c41c31926dca7e))

## [1.7.0](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/compare/v1.6.0...v1.7.0) (2024-08-02)


### Features

* add ably status for ending conversation and post-conversation analytics ([f87491b](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/f87491bb149b3d15f5c5e2984ac1e8f173688c43))* add callsight auth in env files and pipelines yaml ([c81259d](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/c81259d8bfebc43e3dc886611d1cbb6e21f5c270))* add endpoint to retrieve callsight_info ([ed0fd41](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/ed0fd418fb0ab8a122db74686dd18707265016bb))* add whatsapp numnber to flow mapping ([dc14531](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/dc14531a7832f38c5cd0fa4862837213ecf21e53))* Added archival and compress-decompress of flow attributes ([0e10d89](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/0e10d8939e1a366deaa992b4c8b3eb6b8fb9442b))* added support for llama3.1 ([737eb75](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/737eb75d04a5658122081d597832e8914fe8cdff))* integrate callsight postanalytics ([74ada78](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/74ada78e6fbe9e47ae4eaa7237a91bdec3f3891d))* Merge pull request [#53](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/issues/53) from bcgx-pi-deep-ai-core/fix/archival-compress-flows ([580ac3e](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/580ac3e9d1a75eb89f7a5841de44499b2360e1c1))* replaced llama3 models by 3.1 in seed files ([c795faf](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/c795fafc1066f5950985290110a6c21c11a48814))* Use dynamodb batch writer in handle_conversation_flow ([#79](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/issues/79)) ([12ea917](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/12ea9179c75c502bd2c7d8706bbe04149392c81a))

### Bug Fixes

* update import ([59c6da2](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/59c6da236874c0342a5f6b056f0aaf07a83bc544))* update pytests ([2b3ba21](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/2b3ba216ebd1b3864a4387e65a9b1e30a4b28096))* update pytests ([28fef41](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/28fef41bcf9cc13a3fafb25ea7d426e0e9291719))* update whatsapp timestamp type ([d4afb7a](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/d4afb7aa6264210c61f108d8bb4ffaa02eb5236a))* update whatsapp timestamp type ([#60](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/issues/60)) ([59dd638](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/59dd63896f0ccc4fad4a2c8c6966f6f8ba47f8b4))

## [1.6.0](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/compare/v1.5.0...v1.6.0) (2024-07-19)


### Features

* add gpt-4-o mini support ([f47bddb](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/f47bddb0ef44eec3d10d3aee44765e61d1ac3d70))

### Bug Fixes

* Use conversation PK instead of ID to reduce the number of PK parsing expressions ([#49](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/issues/49)) ([74b7c46](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/74b7c46cbc238cfc656504d590fd544568b17236))

## [1.5.0](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/compare/v1.4.0...v1.5.0) (2024-07-17)


### Features

* Add a /start-conversation API endpoint ([#40](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/issues/40)) ([cb49ffc](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/cb49ffcdcd86e9faf55ce11f5b39c825860f6874))

## [1.4.0](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/compare/v1.3.0...v1.4.0) (2024-07-15)


### Features

* add client closing ([bfdf233](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/bfdf233da090dee327a53361037f9dbe4a884cc2))* add openai support ([99e6fc7](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/99e6fc7ddc7043c62f633cc25cb5af89f789dfec))

## [1.3.0](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/compare/v1.2.0...v1.3.0) (2024-07-10)


### Features

* add ability to skip state classifier if 1 or less states ([bc41e1d](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/bc41e1d8e9ac3940ca681ed2c98c52b08e2d0928))* add conversation session bus with shared pubsub ([bbcde18](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/bbcde18cd12548a5e00a3cad233977298b5c50e2))* add new generic genie flow ([8d16e5e](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/8d16e5e481de9d82fd00255cc2b499736420fdd0))

### Bug Fixes

* update tests status code ([6a146e5](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/6a146e5ce76f5e1060d914561395c5db666aea10))

## [1.2.0](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/compare/v1.1.3...v1.2.0) (2024-07-09)


### Features

* Send conversation_ended_flag in agent response ([ffc049d](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/ffc049de5634b44cb005ea475c946c40e18dafaa))* Send conversation_ended_flag in agent response ([ffc049d](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/ffc049de5634b44cb005ea475c946c40e18dafaa))

## [1.1.3](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/compare/v1.1.2...v1.1.3) (2024-07-05)


### Bug Fixes

* Fix a case where backend was crashing due to unexpected None response from handle_conversation_flow ([33658d4](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/33658d442ff34c591f238746f5a5a0e0c8db137a))* Fix keycloak availability issue ([6510113](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/651011357b3119a96997c84b534e90f34cb0fac3))* Remove exposed port from dbinit container ([f24d46c](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/f24d46cfea9552bfccb52b628470d14960193b2b))

## [1.1.2](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/compare/v1.1.1...v1.1.2) (2024-07-02)


### Bug Fixes

* Fix signature expired 500 error ([c9c9580](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/c9c95809c69d0e7aeb829ade38708fdac4feee96))

## [1.1.1](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/compare/v1.1.0...v1.1.1) (2024-07-01)


### Bug Fixes

* Add missing ABLY_API_KEY to db init action ([3dc40ca](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/3dc40ca509cd2ee3475a421b41082dae2a5d84cc))

## [1.1.0](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/compare/v1.0.0...v1.1.0) (2024-07-01)


### Features

* Add a simple websocket agent-response endpoint to use with IVR ([df4e707](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/df4e70725db318c5ebe692f3928d5f912f54657b))* Add conversation_id attribute to agent request payload to enforce conversation ([bd050ec](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/bd050ec3e17675b8831e164209354873235937a3))* Allow websocket client to send an emtpy message to initialize conversation ([f3f01b4](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/f3f01b4acda5d8e0c50efe67b51847bf7346a55b))* Remove login and refresh token endpoints ([f03a65c](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/f03a65c6a7653d9e0b74c13df0b5d34a3471c5c6))* Use Ably to dispatch real time message to admin UI ([8ac3ead](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/8ac3eadd1d7d285b9879a889828ff80daa93e95d))

### Bug Fixes

* cleanup and structure codebase ([#651](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/issues/651)) ([a016a3a](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/a016a3a21dd92106c3145fd2c75f643701fcb456))* Fix compose file after merge ([ec76423](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/ec76423fd4c692482c85927167a790357ed2b662))* fixed the never ending test cases, due to threading lock ([533b223](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/533b223df693a995ffa251acb013b5d65e64afd3))* linting ([065e14d](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/065e14d849ba1107823a3826e2f14c1f3a1bb8fc))* remove coverage files ([172d117](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/172d1177311ef25ead525f0f042ebb3d50befd5a))* remove unused vars ([8821a5a](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/8821a5a22ee583497d77533634074d099ed5bca1))* update .env.example ([bafcb64](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/bafcb648565c410258f1c78afab52c8b35c81c27))* update aws env vars reference for github pipelines ([67b4718](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/67b4718ed0d47ba7b6384594beb6473bdf7de16b))* update calculator nbo unit tests ([7958389](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/795838976b2ede490db9112d3a5153d2dce62a73))* update linting ([0356046](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/0356046180aafc3bebb8f5ef3c0890751b1e18b7))* update linting ([900466c](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/900466c731baba345dc086ed8f5196137813f90f))* update README ([2810e51](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/2810e51cb15667730a8b71c1bc6cad3fc1d51d83))* update README ([64abaeb](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/64abaeb5d71dc529290fea1af3c8708d1f21349c))* update to run only unit tests ([0e89c5b](https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/commit/0e89c5b03356b1a230990cd036dfcd81a57f4183))

## [1.2.0](https://github.com/bcgx-pi-ConnectAI/language-layer/compare/v1.1.0...v1.2.0) (2024-06-12)


### Features

* Updated GP 7 day opening message with recommended_plan_price_after_ca… ([#637](https://github.com/bcgx-pi-ConnectAI/language-layer/issues/637)) ([338b200](https://github.com/bcgx-pi-ConnectAI/language-layer/commit/338b2005080f2fcc8437b67a8796cf72aca54a4f))* Updated gp data volume in calculator utils ([#643](https://github.com/bcgx-pi-ConnectAI/language-layer/issues/643)) ([312d931](https://github.com/bcgx-pi-ConnectAI/language-layer/commit/312d931eb82da9f53491c9b3175756a0022d1d0c))* Updated upsell 7 opening messages and recommended plan price ([#635](https://github.com/bcgx-pi-ConnectAI/language-layer/issues/635)) ([50fdf43](https://github.com/bcgx-pi-ConnectAI/language-layer/commit/50fdf431a1e173fa5e0efb24fc15767b64988bca))* Updated upsell 7 with new packs and removed deprecated variables ([#641](https://github.com/bcgx-pi-ConnectAI/language-layer/issues/641)) ([307c29e](https://github.com/bcgx-pi-ConnectAI/language-layer/commit/307c29ed9d279821334f7a9c6b34a84105d945c3))

### Bug Fixes

* handle iq translation layer ([f2f1617](https://github.com/bcgx-pi-ConnectAI/language-layer/commit/f2f1617ca6845b1662b30379cccd327d10dc830c))* handle iq translation layer ([#639](https://github.com/bcgx-pi-ConnectAI/language-layer/issues/639)) ([e3faa4a](https://github.com/bcgx-pi-ConnectAI/language-layer/commit/e3faa4ad516931ef46a9e713ae7963891cb47549))* update fifo queue params ([01657d8](https://github.com/bcgx-pi-ConnectAI/language-layer/commit/01657d829c7a754b03af6055318e9a57cb340424))* update whatsapp flow states and flow message ([99ab674](https://github.com/bcgx-pi-ConnectAI/language-layer/commit/99ab674c254ef584aecc1dd96d1782cb3dc88acc))* update whatsapp flow states and flow message ([#633](https://github.com/bcgx-pi-ConnectAI/language-layer/issues/633)) ([60911f8](https://github.com/bcgx-pi-ConnectAI/language-layer/commit/60911f8d6de4fd8b6a70d0d5f4e382e56540416f))

## [1.1.0](https://github.com/bcgx-pi-ConnectAI/language-layer/compare/v1.0.0...v1.1.0) (2024-05-29)


### Features

* Batch fetch conversations for 24 hours of given partition date ([ad13043](https://github.com/bcgx-pi-ConnectAI/language-layer/commit/ad130433447fb146efcffedaff38b232efeac45f))* Batch fetch conversations for 24 hours of given partition date ([#599](https://github.com/bcgx-pi-ConnectAI/language-layer/issues/599)) ([15178f2](https://github.com/bcgx-pi-ConnectAI/language-layer/commit/15178f2d575a64699f8775cf24ec1e3e7d64f5be))

## 1.0.0 (2024-05-28)


### Features

* add cart api ([b39de4f](https://github.com/bcgx-pi-ConnectAI/language-layer/commit/b39de4f514263d9f17f0bac2dba87b96a96515ff))* add cart api ([#582](https://github.com/bcgx-pi-ConnectAI/language-layer/issues/582)) ([7098b13](https://github.com/bcgx-pi-ConnectAI/language-layer/commit/7098b13bdb728f551bdf97ccd95131bc6590a5d7))* Add flow soft delete endpoint ([10cf021](https://github.com/bcgx-pi-ConnectAI/language-layer/commit/10cf02143ee1db968c716421b7716077f978dc48))* Add flow versioning to dynamodb PK ([e0a09d2](https://github.com/bcgx-pi-ConnectAI/language-layer/commit/e0a09d216352fce51ef8f08f19d8ba868a6efe14))* add initial version of queue ([3ee7277](https://github.com/bcgx-pi-ConnectAI/language-layer/commit/3ee727711eddb312e6261f9546a0b9857477e5f8))* add iq middleware ([6539b27](https://github.com/bcgx-pi-ConnectAI/language-layer/commit/6539b27d6848d511b850590f004f3744001b6667))* add iq middleware ([#569](https://github.com/bcgx-pi-ConnectAI/language-layer/issues/569)) ([32f38cf](https://github.com/bcgx-pi-ConnectAI/language-layer/commit/32f38cf4d158d57839e960676499fff222e81c7f))* add llm clients fallback ([2877d30](https://github.com/bcgx-pi-ConnectAI/language-layer/commit/2877d309b72b2b111419da22b37575031f014f76))* Add llm clients fallback ([#431](https://github.com/bcgx-pi-ConnectAI/language-layer/issues/431)) ([dd1c1f7](https://github.com/bcgx-pi-ConnectAI/language-layer/commit/dd1c1f7db967c45cc57ea2c7bd42ce672b6900eb))* add user info table and update queue name ([8d0c001](https://github.com/bcgx-pi-ConnectAI/language-layer/commit/8d0c001cf3d3485beef8f1aae13237d065d250b7))* Create a computed field on the Flow pydantic model to return a list of all context variable names ([#396](https://github.com/bcgx-pi-ConnectAI/language-layer/issues/396)) ([1980754](https://github.com/bcgx-pi-ConnectAI/language-layer/commit/1980754dda717bf203256b93d7b38b7d73a7a1c9))* create flow variants ([9847307](https://github.com/bcgx-pi-ConnectAI/language-layer/commit/984730767945415ae86f80fec7d0ebf6182de19d))* Merge static and dynamic context dicts into one context_map object and use topo sort in flow_config to order them ([#390](https://github.com/bcgx-pi-ConnectAI/language-layer/issues/390)) ([d724b6c](https://github.com/bcgx-pi-ConnectAI/language-layer/commit/d724b6c0a09889b4530abfc59889ef41c84b565a))* work queue ([#479](https://github.com/bcgx-pi-ConnectAI/language-layer/issues/479)) ([dcae20f](https://github.com/bcgx-pi-ConnectAI/language-layer/commit/dcae20f6b13239304069f4715c5233467e93166c))

### Bug Fixes

* bootstrap queue before getting the queue url ([6c6abc3](https://github.com/bcgx-pi-ConnectAI/language-layer/commit/6c6abc3dc4754728b352159493873cab395bef9f))* bootstrap queue before getting the queue url ([#482](https://github.com/bcgx-pi-ConnectAI/language-layer/issues/482)) ([538341e](https://github.com/bcgx-pi-ConnectAI/language-layer/commit/538341ee468e4ace340682d2f938f0f9475a3eb6))* Fix SK generation to include trailing # if not all segments are present ([7dcf669](https://github.com/bcgx-pi-ConnectAI/language-layer/commit/7dcf669c683ca6cff94eacb3125db6bbc92edaca))* update reset keywords and functionality ([3977fa7](https://github.com/bcgx-pi-ConnectAI/language-layer/commit/3977fa702c0538fdc13df9eb36f21e1b2d7a02b9))* update reset keywords and functionality ([#593](https://github.com/bcgx-pi-ConnectAI/language-layer/issues/593)) ([9252bc3](https://github.com/bcgx-pi-ConnectAI/language-layer/commit/9252bc32cb69ab836ced6b45f90f4cb3362cf8c1))
