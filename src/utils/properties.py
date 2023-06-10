class ProperiesClass():
    def __init__(self) -> None:
        self.raw= ""
        with open("game.properties", "r", encoding= "utf8") as f:
            self.raw+= f.read()
        self.data: dict[str, any] = {}

        for line in self.raw.split("\n"):
            if line.lstrip().startswith("#") or not line.strip(): continue
            key, value= [v.strip() for v in line.split("=")]
            self.data[key]= eval(value)
    def get(self, key: str):
        return self.data.get(key)

game_properties= ProperiesClass()