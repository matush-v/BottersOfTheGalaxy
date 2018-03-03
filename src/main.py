import random

### CONSTANTS
INSULTS = ["come at me", "who's your daddy", "is this LoL", "cash me outside", "2 + 2 don't know what it is!", "yawn",
           "dis some bullshit"]
FINAL_INSULT = "2 ez. gg. no re"

HERO_DEADPOOL = "DEADPOOL"

ENTITY_TYPE_MINION = "UNIT"
ENTITY_TYPE_HERO = "HERO"
ENTITY_TYPE_TOWER = "TOWER"

### Globals
curInsult = ""
myTeam = None

def play():
    global myTeam
    myTeam = int(input())
    global myTeam

    unused()

    curTurn = 1

    # game loops
    while True:
        gold = int(input())
        enemyGold = int(input())
        roundType = int(input())  # a positive value will show the number of heroes that await a command

        if roundType < 0:
            chooseHero()
            continue

        entityCount = int(input())
        allEntities = readInEntities(entityCount)


        # Write an action using print
        # To debug: print("Debug messages...", file=sys.stderr)


        # If roundType has a negative value then you need to output a Hero name, such as "DEADPOOL" or "VALKYRIE".
        # Else you need to output roundType number of any valid action, such as "WAIT" or "ATTACK unitId"
        printMove("WAIT", curTurn)
        curTurn += 1


def readInEntities(entityCount):
    allEntities = []

    for i in range(entityCount):
        # unitType: UNIT, HERO, TOWER, can also be GROOT from wood1
        # shield: useful in bronze
        # stunDuration: useful in bronze
        # countDown1: all countDown and mana variables are useful starting in bronze
        # heroType: DEADPOOL, VALKYRIE, DOCTOR_STRANGE, HULK, IRONMAN
        # isVisible: 0 if it isn't
        # itemsOwned: useful from wood1
        unitId, team, entityType, x, y, attackRange, health, maxHealth, shield, attackDamage, movementSpeed, stunDuration, goldValue, countDown1, countDown2, countDown3, mana, maxMana, manaRegeneration, heroType, isVisible, itemsOwned = input().split()
        unitId = int(unitId)
        team = int(team)
        x = int(x)
        y = int(y)
        attackRange = int(attackRange)
        health = int(health)
        maxHealth = int(maxHealth)
        shield = int(shield)
        attackDamage = int(attackDamage)
        movementSpeed = int(movementSpeed)
        stunDuration = int(stunDuration)
        goldValue = int(goldValue)
        countDown1 = int(countDown1)
        countDown2 = int(countDown2)
        countDown3 = int(countDown3)
        mana = int(mana)
        maxMana = int(maxMana)
        manaRegeneration = int(manaRegeneration)
        isVisible = int(isVisible)
        itemsOwned = int(itemsOwned)

        entity = None
        if entityType == ENTITY_TYPE_MINION:
            entity = Minion(unitId, team, x, y, attackRange, health, maxHealth, attackDamage, movementSpeed)
        elif entityType == ENTITY_TYPE_HERO:
            entity = Hero(heroType, unitId, team, x, y, attackRange, health, maxHealth, mana, maxMana,
                          attackDamage, movementSpeed, manaRegeneration, isVisible, itemsOwned)
        elif entityType == ENTITY_TYPE_TOWER:
            entity = Tower(unitId, team, x, y)

        if entity is None:
            raise ValueError("unknown entity type " + entityType)

        allEntities.append(entity)

    return allEntities


def chooseHero():
    print HERO_DEADPOOL

def unused():
    bushAndSpawnPointCount = int(
        input())  # usefrul from wood1, represents the number of bushes and the number of places where neutral units can spawn
    for i in range(bushAndSpawnPointCount):
        # entityType: BUSH, from wood1 it can also be SPAWN
        entityType, x, y, radius = input().split()
        x = int(x)
        y = int(y)
        radius = int(radius)
    itemCount = int(input())  # useful from wood2
    for i in range(itemCount):
        # itemName: contains keywords such as BRONZE, SILVER and BLADE, BOOTS connected by "" to help you sort easier
        # itemCost: BRONZE items have lowest cost, the most expensive items are LEGENDARY
        # damage: keyword BLADE is present if the most important item stat is damage
        # moveSpeed: keyword BOOTS is present if the most important item stat is moveSpeed
        # isPotion: 0 if it's not instantly consumed
        itemName, itemCost, damage, health, maxHealth, mana, maxMana, moveSpeed, manaRegeneration, isPotion = input().split()
        itemCost = int(itemCost)
        damage = int(damage)
        health = int(health)
        maxHealth = int(maxHealth)
        mana = int(mana)
        maxMana = int(maxMana)
        moveSpeed = int(moveSpeed)
        manaRegeneration = int(manaRegeneration)
        isPotion = int(isPotion)

def printMove(move, turn):
    global curInsult

    # update insult every 10 turns
    if turn % 10 == 0:
        curInsult = random.choice(INSULTS)

    print(move + ";" + curInsult)




########################################################################################################################
########################################################################################################################
################################################## Classes #############################################################
########################################################################################################################
########################################################################################################################

class Entity(object):

    def __init__(self, unitId, entityType, team, posX, posY, attackRange, health, maxHealth, mana, maxMana, attackDamage, movementSpeed):
        self.unitId = unitId
        self.entityType = entityType
        self.team = team
        self.posX = posX
        self.posY = posY
        self.attackRange = attackRange
        self.health = health
        self.maxHealth = maxHealth
        self.mana = mana
        self.maxMana = maxMana
        self.attackDamage = attackDamage
        self.movementSpeed = movementSpeed

class Minion(Entity):

    def __init__(self, unitId, team, posX, posY, attackRange, health, maxHealth, attackDamage, movementSpeed, mana=0, maxMana=0):
        super(Minion, self).__init__(unitId, ENTITY_TYPE_MINION, team, posX, posY, attackRange, health, maxHealth, mana, maxMana,
                                     attackDamage, movementSpeed)

class Hero(Entity):

    def __init__(self, heroType, unitId, team, posX, posY, attackRange, health, maxHealth, mana, maxMana, attackDamage, movementSpeed, manaRegeneration, isVisible, itemsOwned):
        super(Hero, self).__init__(unitId, ENTITY_TYPE_HERO, team, posX, posY, attackRange, health, maxHealth,
                                   mana, maxMana, attackDamage, movementSpeed)

        self.heroType = heroType
        self.manaRegeneration = manaRegeneration
        self.isVisible = isVisible
        self.itemsOwned = itemsOwned


class Tower(Entity):

    def __init__(self, unitId, team, posX, posY):
        super(Tower, self).__init__(unitId, ENTITY_TYPE_TOWER, team, posX, posY, attackRange=400, health=3000, maxHealth=3000,
                                    mana=0, maxMana=0, attackDamage=100, movementSpeed=0)


play()
