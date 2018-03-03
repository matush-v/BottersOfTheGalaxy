import Entity

class Hero(Entity):

    def __init__(self, itemsOwned, isVisible, heroType, manaRegeneration):
        self.itemsOwned = itemsOwned
        self.isVisible = isVisible
        self.heroType = heroType
        self.manaRegeneration = manaRegeneration


