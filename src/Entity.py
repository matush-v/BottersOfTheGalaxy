class Entity(object):

    def __init__(self, unitId, type, team, attackRange, health, maxHealth, mana, maxMana, attackDamage, movementSpeed, posX, posY):
        self.unitId = unitId
        self.type = type
        self.team = team
        self.attackRange = attackRange
        self.health = health
        self.maxHealth = maxHealth
        self.mana = mana
        self.maxMana = maxMana
        self.attackDamage = attackDamage
        self.movementSpeed = movementSpeed
        self.posX = posX
        self.posY = posY

