import dataclasses
import enum
from dataclasses import dataclass
from decimal import Decimal
from typing import Literal, Optional

from dataclasses_json import dataclass_json
from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator

from genie_dao.datamodel import (
    AIStateType,
    ContextType,
    ContextVariableType,
    LlmModels,
    OutputKey,
)
from genie_dao.datamodel._customers import Customer


class ItemType(enum.Enum):
    """Enum for the item types."""

    FLOW = "FLOW"
    MESSAGE = "MESSAGE"
    CONVERSATION = "CONVERSATION"
    AI_STATE = "AI_STATE"
    STATE_MACHINE = "STATE_MACHINE"
    FLOW_SUPERVISOR = "FLOW_SUPERVISOR"
    METADATA = "METADATA"
    TEMPLATE = "TEMPLATE"
    CONVERSATION_BY_DATE = "CONVERSATION_BY_DATE"
    VARIANT = "VARIANT"
    CALLSIGHT = "CALLSIGHT"
    CUSTOMER_CONTEXT = "CUSTOMER_CONTEXT"


@dataclass
class MessageItem:
    """Message items that are stored in the DB."""

    PK: str
    SK: str
    message_uid: str
    message_sent_datetime: str
    message_type: str
    message_content: str  # Original message content
    message_content_en: str  # Translated message content
    message_detected_language_code: str  # Detected language code
    item_type: str
    item_created_datetime: str


@dataclass
class ConversationItem:
    """Conversation items that are stored in the DB."""

    PK: str
    SK: str
    flow_type: str
    flow_variant_id: str
    conversation_uid: str
    conversation_state: str
    conversation_start_datetime: str
    conversation_end_datetime: str
    user_uid: str
    item_type: str
    item_created_datetime: str


@dataclass
class AIStateItem:
    """AI state items that are stored in the DB."""

    PK: str
    SK: str
    ai_state_name: str
    ai_state_datetime: str
    ai_state_input_message_uid: str
    ai_state_output_message_uid: str
    ai_data_needs: str
    ai_plan_type: str
    ai_number_of_lines: str
    ai_otts: str
    ai_pin_code: str
    ai_existing_services: str
    ai_discussed_plans: str
    ai_other_needs: str
    ai_tone: str
    ai_sentiment: str
    ai_conversation_summary: str
    ai_state_type: str
    item_type: str
    item_created_datetime: str


@dataclass
class CustomerContextItem:
    """Customer context items that are stored in the DB."""

    PK: str
    SK: str
    customer_context: dict
    item_type: str
    item_created_datetime: str


@dataclass
class CallsightItem:
    """Callsight items that are stored in the DB."""

    PK: str
    SK: str
    callsight_str_response: str
    item_type: str
    item_created_datetime: str


@dataclass
class ConversationAIStateItem:
    """Conversation with AI state items that are stored in the DB."""

    conversation_item: ConversationItem
    ai_state_item: Optional[AIStateItem] = None
    customer_context_item: Optional[CustomerContextItem] = None


@dataclass
class ConversationCount:
    """Conversation count that are stored in the DB."""

    today: int
    yesterday: int


@dataclass
class ConversationTableFilterItem:
    """Conversation table filter item that are stored in the DB."""

    flow_type: list[str]
    flow_variant_id: list[str]


class FlowStateMachineFlowSupervisor(BaseModel):
    max_total_unrelated_state_count: int = 0
    max_consecutive_unrelated_state_count: int = 0
    enabled: bool = False


class FlowCallSightConfig(BaseModel):
    enabled: bool = False


class VariantConfig(BaseModel):
    variants_weights: list[int]


@dataclasses.dataclass
class FlowPK:
    version_number: int = 1

    @classmethod
    def parse(cls, pk: str):
        split = pk.split("#")
        return cls(version_number=int(split[1]))

    def __str__(self):
        pk_segments = [ItemType.FLOW.value, str(self.version_number)]
        return "#".join(pk_segments)


@dataclasses.dataclass
class FlowVariantID:
    variant_number: int

    @classmethod
    def parse(cls, variant_id):
        split = variant_id.split("_")
        return cls(variant_number=int(split[1]))

    def __str__(self):
        return f"{ItemType.VARIANT.value}_{self.variant_number}"


class BaseFlowSK:
    @staticmethod
    def generate(potential_segments: list[str]):
        sk_segments = []

        for segment in potential_segments:
            if segment is None:
                break
            sk_segments.append(segment)

        if len(sk_segments) < len(potential_segments):
            """Force a trailing # character if not all segments are present."""
            sk_segments.append("")

        return "#".join(sk_segments)


@dataclasses.dataclass
class FlowVariantSK(BaseFlowSK):
    flow_id: Optional[str] = None
    variant_id: Optional[str] = None
    datetime: Optional[str] = None

    @classmethod
    def parse(cls, sk: str):
        split = sk.split("#")
        return cls(flow_id=split[1], variant_id=split[2], datetime=split[3])

    def __str__(self):
        return self.generate([ItemType.METADATA.value, self.flow_id, self.variant_id, self.datetime])


@dataclasses.dataclass
class FlowTemplateVariantSK(BaseFlowSK):
    template_id: Optional[str] = None
    variant_id: Optional[str] = None
    datetime: Optional[str] = None

    @classmethod
    def parse(cls, sk: str):
        split = sk.split("#")
        return cls(template_id=split[2], variant_id=split[3], datetime=split[4])

    def __str__(self):
        return self.generate(
            [
                ItemType.TEMPLATE.value,
                ItemType.METADATA.value,
                self.template_id,
                self.variant_id,
                self.datetime,
            ]
        )


class FlowStateMachineConfig(BaseModel):
    is_ai_first_message: bool
    translation_service_enabled: bool
    message_timeout_s: int = 900
    variants_config: VariantConfig
    hard_coded_transitions: Optional[dict[str, list[str]]] = {}
    flow_supervisor: FlowStateMachineFlowSupervisor
    callsight: Optional[FlowCallSightConfig] = FlowCallSightConfig(enabled=False)


class FlowStateMachineState(BaseModel):
    next_states: list[str]


class FlowStateMachine(BaseModel):
    FlowConfig: FlowStateMachineConfig
    FlowStates: dict[str, FlowStateMachineState]


class FlowStateFlowPrompt(BaseModel):
    instructions: str
    user_command: str
    ai_model: LlmModels = LlmModels.LLAMA3_70B.value

    class Config:
        use_enum_values = True


class PromptExample(BaseModel):
    role: str
    content: str


class FlowStateUtilityPrompt(BaseModel):
    instructions: str
    example: Optional[list[PromptExample]] = []
    user_command: str


class FlowStateRetrieverTemplate(BaseModel):
    name: str
    ai_model: LlmModels

    class Config:
        use_enum_values = True


class FlowStateRetriever(BaseModel):
    template: FlowStateRetrieverTemplate


class FlowStatePrompts(BaseModel):
    FLOW: Optional[FlowStateFlowPrompt] = None
    RETRIEVERS: list[FlowStateRetriever]

    @field_validator("RETRIEVERS")
    @classmethod
    def retrievers_must_contain_state_classifier(cls, v: list[FlowStateRetriever]):
        has_state_classifier = any(r.template.name == "STATE_CLASSIFIER" for r in v)
        if not has_state_classifier:
            raise ValueError("STATE_CLASSIFIER retriever must be present in RETRIEVERS field")
        return v


class FlowStateMetadata(BaseModel):
    is_static_response: Optional[bool] = False
    static_response: Optional[str] = None
    state_description: str
    state_next_goal: str
    ai_state_type: AIStateType
    state_prompts: FlowStatePrompts

    class Config:
        use_enum_values = True


class FlowContext(BaseModel):
    value: str
    context_type: ContextType

    class Config:
        use_enum_values = True


class DeepgramModel(enum.StrEnum):
    Nova_2 = "nova-2"


class DeepgramLanguage(enum.StrEnum):
    Bulgarian = "bg"
    Catalan = "ca"
    ChineseMandarinSimplified = "zh-CN"
    ChineseMandarinTraditional = "zh-TW"
    ChineseCantoneseTraditional = "zh-HK"
    Czech = "cs"
    Danish = "da"
    Dutch = "nl"
    English = "en"
    EnglishAustralian = "en-AU"
    EnglishBritish = "en-GB"
    EnglishUs = "en-US"
    EnglishNewZealand = "en-NZ"
    Estonian = "et"
    Finnish = "fi"
    Flemish = "nl-BE"
    French = "fr"
    FrenchCanadian = "fr-CA"
    German = "de"
    GermanSwitzerland = "de-CH"
    Greek = "el"
    Hindi = "hi"
    Hungarian = "hu"
    Indonesian = "id"
    Italian = "it"
    Japanese = "ja"
    Korean = "ko"
    Latvian = "lv"
    Lithuanian = "lt"
    Malay = "ms"
    MultilingualSpanishEnglish = "multi"
    Norwegian = "no"
    Polish = "pl"
    Portuguese = "pt"
    PortugueseBrazilian = "pt-BR"
    Romanian = "ro"
    Russian = "ru"
    Slovak = "sk"
    Spanish = "es"
    Swedish = "sv"
    Thai = "th"
    Turkish = "tr"
    Ukrainian = "uk"
    Vietnamese = "vi"


class AwsTranscribeLanguage(enum.StrEnum):
    EnglishAustralian = "en-AU"
    EnglishBritish = "en-GB"
    EnglishUS = "en-US"
    French = "fr-FR"
    FrenchCanadian = "fr-CA"
    German = "de-DE"
    HindiIndian = "hi-IN"
    Italian = "it-IT"
    Japanese = "ja-JP"
    Korean = "ko-KR"
    PortugueseBrazilian = "pt-BR"
    SpanishUs = "es-US"
    Thai = "th-TH"
    ChineseSimplified = "zh-CN"


class FlowVoiceConfigDeepgramParams(BaseModel):
    model: DeepgramModel = DeepgramModel.Nova_2
    language: DeepgramLanguage = DeepgramLanguage.English


class FlowVoiceConfigAwsTranscribeParams(BaseModel):
    language: AwsTranscribeLanguage = AwsTranscribeLanguage.EnglishUS

    @field_validator("language", mode="before")
    @classmethod
    def omit_invalid_languages(cls, language: dict[AwsTranscribeLanguage]):
        # fr is invalid language
        if language == "fr":
            return AwsTranscribeLanguage.French
        if language in AwsTranscribeLanguage.__members__.values():
            return language
        return AwsTranscribeLanguage.EnglishUS


class AzureLanguage(enum.StrEnum):
    Afrikaans = "af-ZA"
    Amharic = "am-ET"
    Arabic = "ar-AE"
    Azerbaijani = "az-AZ"
    Bulgarian = "bg-BG"
    Bengali = "bn-IN"
    Bosnian = "bs-BA"
    Catalan = "ca-ES"
    Czech = "cs-CZ"
    Welsh = "cy-GB"
    Danish = "da-DK"
    German = "de-DE"
    Greek = "el-GR"
    EnglishAustralia = "en-AU"
    EnglishUnitedKingdom = "en-GB"
    EnglishNewZealand = "en-NZ"
    EnglishUnitedStates = "en-US"
    SpanishSpain = "es-ES"
    Estonian = "et-EE"
    Basque = "eu-ES"
    Persian = "fa-IR"
    Finnish = "fi-FI"
    Filipino = "fil-PH"
    FrenchFrance = "fr-FR"
    Irish = "ga-IE"
    Galician = "gl-ES"
    Gujarati = "gu-IN"
    Hebrew = "he-IL"
    Hindi = "hi-IN"
    Croatian = "hr-HR"
    Hungarian = "hu-HU"
    Armenian = "hy-AM"
    Indonesian = "id-ID"
    Icelandic = "is-IS"
    ItalianItaly = "it-IT"
    Japanese = "ja-JP"
    Javanese = "jv-ID"
    Georgian = "ka-GE"
    Kazakh = "kk-KZ"
    Khmer = "km-KH"
    Kannada = "kn-IN"
    Korean = "ko-KR"
    Lao = "lo-LA"
    Lithuanian = "lt-LT"
    Latvian = "lv-LV"
    Macedonian = "mk-MK"
    Malayalam = "ml-IN"
    Mongolian = "mn-MN"
    Marathi = "mr-IN"
    Malay = "ms-MY"
    Maltese = "mt-MT"
    Burmese = "my-MM"
    NorwegianBokmål = "nb-NO"
    Nepali = "ne-NP"
    DutchBelgium = "nl-BE"
    DutchNetherlands = "nl-NL"
    Punjabi = "pa-IN"
    Polish = "pl-PL"
    Pashto = "ps-AF"
    PortugueseBrazil = "pt-BR"
    PortuguesePortugal = "pt-PT"
    Romanian = "ro-RO"
    Russian = "ru-RU"
    Sinhala = "si-LK"
    Slovak = "sk-SK"
    Slovenian = "sl-SI"
    Somali = "so-SO"
    Albanian = "sq-AL"
    Serbian = "sr-RS"
    Swedish = "sv-SE"
    KiswahiliKenya = "sw-KE"
    KiswahiliTanzania = "sw-TZ"
    Tamil = "ta-IN"
    Telugu = "te-IN"
    Thai = "th-TH"
    Turkish = "tr-TR"
    Ukrainian = "uk-UA"
    Urdu = "ur-IN"
    Uzbek = "uz-UZ"
    Vietnamese = "vi-VN"
    isiZulu = "zu-ZA"


class FlowVoiceConfigSttAzureParams(BaseModel):
    language: AzureLanguage = AzureLanguage.EnglishUnitedStates


class FlowVoiceConfigSttPlatform(enum.StrEnum):
    Deepgram = "deepgram"
    AwsTranscribe = "aws_transcribe"
    Azure = "azure"


class FlowVoiceConfigTtsPlatform(enum.StrEnum):
    Elevenlabs = "elevenlabs"
    Cartesia = "cartesia"
    Azure = "azure"


class FlowVoiceConfigSpeechToText(BaseModel):
    platform: FlowVoiceConfigSttPlatform = FlowVoiceConfigSttPlatform.AwsTranscribe
    deepgram_params: FlowVoiceConfigDeepgramParams = Field(default_factory=FlowVoiceConfigDeepgramParams)
    aws_transcribe_params: FlowVoiceConfigAwsTranscribeParams = Field(
        default_factory=FlowVoiceConfigAwsTranscribeParams
    )
    azure_params: FlowVoiceConfigSttAzureParams = Field(default_factory=FlowVoiceConfigSttAzureParams)


class FlowVoiceConfigElevenlabsModels(enum.StrEnum):
    ELEVEN_TURBO_V2_5 = "eleven_turbo_v2_5"


class ElevenlabsLanguage(enum.StrEnum):
    Arabic = "ar"
    Bulgarian = "bg"
    Chinese = "zh"
    Croatian = "hr"
    Czech = "cs"
    Danish = "da"
    Dutch = "nl"
    English = "en"
    Filipino = "fil"
    Finnish = "fi"
    French = "fr"
    German = "de"
    Greek = "el"
    Hindi = "hi"
    Indonesian = "id"
    Italian = "it"
    Japanese = "ja"
    Korean = "ko"
    Malay = "ms"
    Polish = "pl"
    Portuguese = "pt"
    Romanian = "ro"
    Russian = "ru"
    Slovak = "sk"
    Spanish = "es"
    Swedish = "sv"
    Tamil = "ta"
    Turkish = "tr"
    Ukrainian = "uk"


class FlowVoiceConfigElevenlabsParams(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    model_id: FlowVoiceConfigElevenlabsModels = FlowVoiceConfigElevenlabsModels.ELEVEN_TURBO_V2_5
    voice_id: Optional[str] = None
    language_code: ElevenlabsLanguage | None = None
    stability: Decimal = Field(Decimal("0.7"), ge=Decimal("0.0"), le=Decimal("1.0"), multiple_of=Decimal("0.1"))
    similarity_boost: Decimal = Field(Decimal("0.8"), ge=Decimal("0.0"), le=Decimal("1.0"), multiple_of=Decimal("0.1"))


class FlowVoiceConfigCartesiaModels(enum.StrEnum):
    SONIC_ENGLISH = "sonic-english"
    SONIC_MULTILINGUAL = "sonic-multilingual"


class FlowVoiceConfigCartesiaParams(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    model_id: FlowVoiceConfigCartesiaModels = FlowVoiceConfigCartesiaModels.SONIC_ENGLISH
    voice_id: Optional[str] = None


class AzureVoiceName(enum.StrEnum):
    af_ZA_AdriNeural = "af-ZA-AdriNeural"
    af_ZA_WillemNeural = "af-ZA-WillemNeural"
    am_ET_MeklitNeural = "am-ET-MeklitNeural"
    am_ET_AmehaNeural = "am-ET-AmehaNeural"
    ar_AE_FatimaNeural = "ar-AE-FatimaNeural"
    ar_AE_HamdanNeural = "ar-AE-HamdanNeural"
    az_AZ_BanuNeural = "az-AZ-BanuNeural"
    az_AZ_BabekNeural = "az-AZ-BabekNeural"
    bg_BG_KalinaNeural = "bg-BG-KalinaNeural"
    bg_BG_BorislavNeural = "bg-BG-BorislavNeural"
    bn_IN_TanishaaNeural = "bn-IN-TanishaaNeural"
    bn_IN_BashkarNeural = "bn-IN-BashkarNeural"
    bs_BA_VesnaNeural = "bs-BA-VesnaNeural"
    bs_BA_GoranNeural = "bs-BA-GoranNeural"
    ca_ES_AlbaNeural = "ca-ES-AlbaNeural"
    ca_ES_EnricNeural = "ca-ES-EnricNeural"
    cs_CZ_VlastaNeural = "cs-CZ-VlastaNeural"
    cs_CZ_AntoninNeural = "cs-CZ-AntoninNeural"
    cy_GB_NiaNeural = "cy-GB-NiaNeural"
    cy_GB_AledNeural = "cy-GB-AledNeural"
    da_DK_ChristelNeural = "da-DK-ChristelNeural"
    da_DK_JeppeNeural = "da-DK-JeppeNeural"
    de_DE_KatjaNeural = "de-DE-KatjaNeural"
    de_DE_ConradNeural = "de-DE-ConradNeural"
    el_GR_AthinaNeural = "el-GR-AthinaNeural"
    el_GR_NestorasNeural = "el-GR-NestorasNeural"
    en_AU_NatashaNeural = "en-AU-NatashaNeural"
    en_AU_WilliamNeural = "en-AU-WilliamNeural"
    en_GB_LibbyNeural = "en-GB-LibbyNeural"
    en_GB_RyanNeural = "en-GB-RyanNeural"
    en_NZ_MollyNeural = "en-NZ-MollyNeural"
    en_NZ_MitchellNeural = "en-NZ-MitchellNeural"
    en_US_AriaNeural = "en-US-AriaNeural"
    en_US_JennyNeural = "en-US-JennyNeural"
    en_US_GuyNeural = "en-US-GuyNeural"
    es_ES_LiaNeural = "es-ES-LiaNeural"
    es_ES_TeoNeural = "es-ES-TeoNeural"
    es_ES_ElviraNeural = "es-ES-ElviraNeural"
    es_ES_AlvaroNeural = "es-ES-AlvaroNeural"
    es_ES_XimenaNeural = "es-ES-XimenaNeural"
    es_ES_XimenaMultilingualNeural = "es-ES-XimenaMultilingualNeural"
    et_EE_AnuNeural = "et-EE-AnuNeural"
    et_EE_KertNeural = "et-EE-KertNeural"
    eu_ES_MirenNeural = "eu-ES-MirenNeural"
    eu_ES_AitorNeural = "eu-ES-AitorNeural"
    fa_IR_DaryaNeural = "fa-IR-DaryaNeural"
    fa_IR_FaridNeural = "fa-IR-FaridNeural"
    fi_FI_NooraNeural = "fi-FI-NooraNeural"
    fi_FI_HarriNeural = "fi-FI-HarriNeural"
    fil_PH_BlessicaNeural = "fil-PH-BlessicaNeural"
    fil_PH_AngeloNeural = "fil-PH-AngeloNeural"
    fr_FR_DeniseNeural = "fr-FR-DeniseNeural"
    fr_FR_HenriNeural = "fr-FR-HenriNeural"
    ga_IE_OrlaNeural = "ga-IE-OrlaNeural"
    ga_IE_ColmNeural = "ga-IE-ColmNeural"
    gl_ES_SabelaNeural = "gl-ES-SabelaNeural"
    gl_ES_RoiNeural = "gl-ES-RoiNeural"
    gu_IN_DhwaniNeural = "gu-IN-DhwaniNeural"
    gu_IN_NiranjanNeural = "gu-IN-NiranjanNeural"
    he_IL_HilaNeural = "he-IL-HilaNeural"
    he_IL_AvriNeural = "he-IL-AvriNeural"
    hi_IN_SwaraNeural = "hi-IN-SwaraNeural"
    hi_IN_MadhurNeural = "hi-IN-MadhurNeural"
    hr_HR_GabrijelaNeural = "hr-HR-GabrijelaNeural"
    hr_HR_SreckoNeural = "hr-HR-SreckoNeural"
    hu_HU_NoemiNeural = "hu-HU-NoemiNeural"
    hu_HU_TamasNeural = "hu-HU-TamasNeural"
    hy_AM_AnahitNeural = "hy-AM-AnahitNeural"
    hy_AM_HaykNeural = "hy-AM-HaykNeural"
    id_ID_GadisNeural = "id-ID-GadisNeural"
    id_ID_ArdiNeural = "id-ID-ArdiNeural"
    is_IS_GudrunNeural = "is-IS-GudrunNeural"
    is_IS_GunnarNeural = "is-IS-GunnarNeural"
    it_IT_ElsaNeural = "it-IT-ElsaNeural"
    it_IT_DiegoNeural = "it-IT-DiegoNeural"
    ja_JP_NanamiNeural = "ja-JP-NanamiNeural"
    ja_JP_KeitaNeural = "ja-JP-KeitaNeural"
    jv_ID_DamayantiNeural = "jv-ID-DamayantiNeural"
    jv_ID_SuryaNeural = "jv-ID-SuryaNeural"
    ka_GE_EkaNeural = "ka-GE-EkaNeural"
    ka_GE_GiorgiNeural = "ka-GE-GiorgiNeural"
    kk_KZ_AigulNeural = "kk-KZ-AigulNeural"
    kk_KZ_DauletNeural = "kk-KZ-DauletNeural"
    km_KH_SreymomNeural = "km-KH-SreymomNeural"
    km_KH_SinaNeural = "km-KH-SinaNeural"
    kn_IN_SapnaNeural = "kn-IN-SapnaNeural"
    kn_IN_GaganNeural = "kn-IN-GaganNeural"
    ko_KR_SunHiNeural = "ko-KR-SunHiNeural"
    ko_KR_InJoonNeural = "ko-KR-InJoonNeural"
    lo_LA_ChanNeural = "lo-LA-ChanNeural"
    lo_LA_VithNeural = "lo-LA-VithNeural"
    lt_LT_OnaNeural = "lt-LT-OnaNeural"
    lt_LT_LeonasNeural = "lt-LT-LeonasNeural"
    lv_LV_EveritaNeural = "lv-LV-EveritaNeural"
    lv_LV_NilsNeural = "lv-LV-NilsNeural"
    mk_MK_MaryaNeural = "mk-MK-MaryaNeural"
    mk_MK_AleksandarNeural = "mk-MK-AleksandarNeural"
    ml_IN_SobhanaNeural = "ml-IN-SobhanaNeural"
    ml_IN_MidhunNeural = "ml-IN-MidhunNeural"
    mn_MN_AltantsetsegNeural = "mn-MN-AltantsetsegNeural"
    mn_MN_BataaNeural = "mn-MN-BataaNeural"
    mr_IN_AarohiNeural = "mr-IN-AarohiNeural"
    mr_IN_ManoharNeural = "mr-IN-ManoharNeural"
    ms_MY_YasminNeural = "ms-MY-YasminNeural"
    ms_MY_OsmanNeural = "ms-MY-OsmanNeural"
    mt_MT_GraceNeural = "mt-MT-GraceNeural"
    mt_MT_JosephNeural = "mt-MT-JosephNeural"
    my_MM_ThiriNeural = "my-MM-ThiriNeural"
    my_MM_NyeinNeural = "my-MM-NyeinNeural"
    nb_NO_IselinNeural = "nb-NO-IselinNeural"
    nb_NO_FinnNeural = "nb-NO-FinnNeural"
    ne_NP_NimalaNeural = "ne-NP-NimalaNeural"
    ne_NP_SuryaNeural = "ne-NP-SuryaNeural"
    nl_BE_DenaNeural = "nl-BE-DenaNeural"
    nl_BE_ArnaudNeural = "nl-BE-ArnaudNeural"
    nl_NL_ColetteNeural = "nl-NL-ColetteNeural"
    nl_NL_MaartenNeural = "nl-NL-MaartenNeural"
    pa_IN_KajalNeural = "pa-IN-KajalNeural"
    pa_IN_JaswinderNeural = "pa-IN-JaswinderNeural"
    pl_PL_ZofiaNeural = "pl-PL-ZofiaNeural"
    pl_PL_MarekNeural = "pl-PL-MarekNeural"
    ps_AF_LinaNeural = "ps-AF-LinaNeural"
    ps_AF_WaliNeural = "ps-AF-WaliNeural"
    pt_BR_FranciscaNeural = "pt-BR-FranciscaNeural"
    pt_BR_AntonioNeural = "pt-BR-AntonioNeural"
    pt_PT_FernandaNeural = "pt-PT-FernandaNeural"
    pt_PT_RaulNeural = "pt-PT-RaulNeural"
    ro_RO_AlinaNeural = "ro-RO-AlinaNeural"
    ro_RO_EmilNeural = "ro-RO-EmilNeural"
    ru_RU_SvetlanaNeural = "ru-RU-SvetlanaNeural"
    ru_RU_DmitryNeural = "ru-RU-DmitryNeural"
    si_LK_TharukaNeural = "si-LK-TharukaNeural"
    si_LK_SameeraNeural = "si-LK-SameeraNeural"
    sk_SK_ViktoriaNeural = "sk-SK-ViktoriaNeural"
    sk_SK_LukasNeural = "sk-SK-LukasNeural"
    sl_SI_PetraNeural = "sl-SI-PetraNeural"
    sl_SI_RokNeural = "sl-SI-RokNeural"
    so_SO_MaryanNeural = "so-SO-MaryanNeural"
    so_SO_MuuseNeural = "so-SO-MuuseNeural"
    sq_AL_AnilaNeural = "sq-AL-AnilaNeural"
    sq_AL_IliNeural = "sq-AL-IliNeural"
    sr_RS_SaraNeural = "sr-RS-SaraNeural"
    sr_RS_NikolaNeural = "sr-RS-NikolaNeural"
    sv_SE_HedvigNeural = "sv-SE-HedvigNeural"
    sv_SE_MattiasNeural = "sv-SE-MattiasNeural"
    sw_KE_RafikiNeural = "sw-KE-RafikiNeural"
    sw_KE_ChangawaNeural = "sw-KE-ChangawaNeural"
    sw_TZ_RehemaNeural = "sw-TZ-RehemaNeural"
    sw_TZ_DaudiNeural = "sw-TZ-DaudiNeural"
    ta_IN_PallaviNeural = "ta-IN-PallaviNeural"
    ta_IN_ValluvarNeural = "ta-IN-ValluvarNeural"
    te_IN_ShrutiNeural = "te-IN-ShrutiNeural"
    te_IN_MohanNeural = "te-IN-MohanNeural"
    th_TH_AcharaNeural = "th-TH-AcharaNeural"
    th_TH_PawatNeural = "th-TH-PawatNeural"
    tr_TR_EmelNeural = "tr-TR-EmelNeural"
    tr_TR_AhmetNeural = "tr-TR-AhmetNeural"
    uk_UA_PolinaNeural = "uk-UA-PolinaNeural"
    uk_UA_OstapNeural = "uk-UA-OstapNeural"
    ur_IN_GulNeural = "ur-IN-GulNeural"
    ur_IN_AyubNeural = "ur-IN-AyubNeural"
    uz_UZ_MadinaNeural = "uz-UZ-MadinaNeural"
    uz_UZ_SardorNeural = "uz-UZ-SardorNeural"
    vi_VN_HoaiMyNeural = "vi-VN-HoaiMyNeural"
    vi_VN_NamMinhNeural = "vi-VN-NamMinhNeural"
    zu_ZA_ThandoNeural = "zu-ZA-ThandoNeural"
    zu_ZA_ThembaNeural = "zu-ZA-ThembaNeural"


class FlowVoiceConfigTtsAzureParams(BaseModel):
    language: AzureLanguage = AzureLanguage.EnglishUnitedStates
    voice_name: AzureVoiceName = AzureVoiceName.en_US_AriaNeural


class FlowVoiceConfigTextToSpeech(BaseModel):
    platform: FlowVoiceConfigTtsPlatform = FlowVoiceConfigTtsPlatform.Elevenlabs
    elevenlabs_params: FlowVoiceConfigElevenlabsParams = Field(default_factory=FlowVoiceConfigElevenlabsParams)
    cartesia_params: FlowVoiceConfigCartesiaParams = Field(default_factory=FlowVoiceConfigCartesiaParams)
    azure_params: FlowVoiceConfigTtsAzureParams = Field(default_factory=FlowVoiceConfigTtsAzureParams)


class FlowVoiceConfig(BaseModel):
    post_call_analytics_timeout: int = 30
    voice_interruptions_enabled: bool = True
    voice_interruptions_min_words: int = 2
    ignore_user_messages_during_agent_speech: bool = False
    ambience_noice_level: int = 500
    speech_to_text: FlowVoiceConfigSpeechToText = Field(default_factory=FlowVoiceConfigSpeechToText)
    text_to_speech: FlowVoiceConfigTextToSpeech = Field(default_factory=FlowVoiceConfigTextToSpeech)


class FlowContextVariable(BaseModel):
    id: str
    context_var_type: ContextVariableType

    class Config:
        use_enum_values = True


class Flow(BaseModel):
    """State machine items that are stored in the DB."""

    PK: str
    SK: str
    flow_states: dict[str, FlowStateMetadata]
    flow_state_machine: FlowStateMachine
    flow_context_map: dict[str, FlowContext]
    flow_base_config: str
    flow_config_llm_prompts: dict[str, str]
    flow_utility_prompts: dict[str, FlowStateUtilityPrompt]
    flow_display_name: Optional[str] = ""
    flow_description: Optional[str] = ""
    item_type: str
    item_created_datetime: str
    item_deleted_datetime: Optional[str] = None
    channel: Optional[str]
    product_segment: Optional[str]
    experience_type: Optional[Literal["System Template", "Custom Template", "Custom Experience"]]
    callsight_pipeline: Optional[dict] = None
    voice_config: FlowVoiceConfig = Field(default_factory=FlowVoiceConfig)

    @computed_field
    @property
    def flow_context_variables(self) -> list[FlowContextVariable]:
        user_defined_vars = [
            FlowContextVariable(id=context_id, context_var_type=ContextVariableType.USER_DEFINED)
            for context_id, _ in self.flow_context_map.items()
        ]

        blacklisted_output_vars = (
            OutputKey.STATE_CLASSIFIER.value,
            OutputKey.FLOW.value,
        )
        utilities_output_vars = [
            FlowContextVariable(id=var_name, context_var_type=ContextVariableType.UTILITIES_OUTPUT)
            for var_name in OutputKey
            if var_name not in blacklisted_output_vars
        ]

        api_vars = [
            FlowContextVariable(id=var_name.name, context_var_type=ContextVariableType.API)
            for var_name in dataclasses.fields(Customer)
        ]

        return user_defined_vars + utilities_output_vars + api_vars

    @field_validator("flow_states")
    @classmethod
    def retrievers_all_or_none_contain_summary(cls, flow_states: dict[str, FlowStateMetadata]):
        """Validate that either all states have summary utility, or no states have
        summary utility."""
        state_count = len(flow_states)
        summary_count = sum(
            [
                any(retriever.template.name == OutputKey.SUMMARY.value for retriever in state.state_prompts.RETRIEVERS)
                for state in flow_states.values()
            ]
        )
        if summary_count != 0 and summary_count != state_count:
            raise ValueError(
                f"There are {state_count} states, and only {summary_count} of them have summary. Either all states have summary, or no states have summary."
            )
        return flow_states

    def __str__(self) -> str:
        return f"PK: {self.PK}, SK: {self.SK}, flow_display_name: {self.flow_display_name}"

    def extract_flow_variant_id(self) -> str:
        """Extract the flow variant id from the SK."""
        return self.SK.split("#")[-2]

    class Config:
        extra = "forbid"


@dataclass
class FlowSupervisorItem:
    """Flow supervisor items that are stored in the DB."""

    PK: str
    SK: str
    flow_supervisor_uid: str
    flow_supervisor_state_datetime: str
    total_unrelated_state_count: int
    consecutive_unrelated_state_count: int
    item_type: str
    item_created_datetime: str


@dataclass
@dataclass_json
class LastEvaluatedKey:
    SK: str
    PK: str
    item_type: str
