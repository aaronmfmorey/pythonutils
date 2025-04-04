from dotenv import dotenv_values

class DotEnvToKeysFile:
    def __init__(self):
        pass

    @staticmethod
    def create_file(path):
        config = dotenv_values(".env")
        with open(f"{path}/.env.sample", "w") as text_file:
            for k, v in config.items():
                text_file.write(f"{k}=\n")