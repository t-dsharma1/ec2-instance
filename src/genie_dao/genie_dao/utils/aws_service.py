import logging

import aioboto3
from botocore.exceptions import BotoCoreError, ClientError


class AWSServiceHandler:
    def __init__(self, service_name, **kwargs):
        self.service_name = service_name
        self.kwargs = kwargs

    async def get_client(self):
        # Simply return the client creation coroutine, to be used with 'async with'
        return aioboto3.client(service_name=self.service_name, **self.kwargs)


class AWSTranslationHandler(AWSServiceHandler):
    def __init__(self, **kwargs):
        super().__init__(service_name="translate", **kwargs)

    async def translate_text(self, text, source_language_code, target_language_code):
        # Using 'async with' directly with aioboto3.client() call
        async with aioboto3.Session().client(service_name=self.service_name, **self.kwargs) as client:
            try:
                # Read the terminology file
                # current_directory = os.path.dirname(os.path.realpath(__file__))
                # file_dir = os.path.join(current_directory, "terminology.csv")
                # with open(file_dir, "rb") as f:
                #     data = f.read()

                # file_data = bytearray(data)
                # # Directly call the method on the client
                # await client.import_terminology(
                #     Name="terminology", MergeStrategy="OVERWRITE", TerminologyData={"File": file_data, "Format": "CSV"}
                # )
                response = await client.translate_text(
                    Text=text,
                    TerminologyNames=["terminology"],
                    SourceLanguageCode=source_language_code,
                    TargetLanguageCode=target_language_code,
                )
                return response
            except BotoCoreError as e:
                logging.error(f"BotoCoreError in translate_text: {e}")
                raise
            except ClientError as e:
                logging.error(f"ClientError in translate_text: {e}")
                raise
            except Exception as e:
                logging.error(f"Unexpected error in translate_text: {e}")
                raise


# Example usage (must be run in an asyncio environment):
# import asyncio
# async def main():
#     translator = AWSTranslationHandler()
#     translation = await translator.translate_text("Hello, world!", "en", "fr")
#     print(translation)
#
# asyncio.run(main())
