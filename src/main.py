import random
import sys
import math
import copy

### CONSTANTS
INSULTS = ["come at me", "who's your daddy", "is this LoL", "cash me outside", "2 + 2 don't know what it is!", "yawn",
           "dis some disrespect"]
# TODO: use this at the end (not sure how we know when the end is....maybe when tower or hero is at a low health?)
FINAL_INSULT = "2 ez. gg. no re"

UNUSED_HEROES = ["DEADPOOL", "IRONMAN", "HULK", "VALKYRIE", "DOCTOR_STRANGE"]
CHOSEN_ALIVE_HEROES = []

ENTITY_TYPE_MINION = "UNIT"
ENTITY_TYPE_HERO = "HERO"
ENTITY_TYPE_TOWER = "TOWER"
ENTITY_TYPE_GROOT = "GROOT"

ACTION_WAIT = "WAIT"
ACTION_MOVE = "MOVE"
ACTION_ATTACK = "ATTACK"
ACTION_ATTACK_NEAREST = "ATTACK_NEAREST"
ACTION_MOVE_ATTACK = "MOVE_ATTACK"
ACTION_BUY = "BUY"
ACTION_SELL = "SELL"

### Globals
curInsult = ""
myTeam = 0
allEntities = []
myGold = 0

def play():
    global myTeam, allEntities, myGold
    myTeam = int(raw_input())

    unused()

    itemCount = int(raw_input())  # useful from wood2
    readInItems(itemCount)
    curTurn = 1

    # game loops
    while True:
        debug("curTurn " + `curTurn`)

        myGold = int(raw_input())
        enemyGold = int(raw_input())
        roundType = int(raw_input())

        # If roundType has a negative value then you need to output a Hero name, such as "DEADPOOL" or "VALKYRIE".
        if roundType < 0:
            chooseHero()

        # Else you need to output roundType number of any valid action, such as "WAIT" or "ATTACK unitId"
        entityCount = int(raw_input())
        readInEntities(entityCount)

        # a positive value will show the number of heroes that await a command
        if roundType > 0:
            updateMyHeroes()
            for heroIndex in xrange(roundType):
                curHero = getHeroByType(myTeam, CHOSEN_ALIVE_HEROES[heroIndex])
                executeTurn(curTurn, curHero)
            curTurn += 1


def updateMyHeroes():
    myAliveHeroes = getHeroes(myTeam)
    for heroType in CHOSEN_ALIVE_HEROES:
        if not containsHeroOfType(myAliveHeroes, heroType):
            CHOSEN_ALIVE_HEROES.remove(heroType)


def containsHeroOfType(heroes, heroType):
    for h in heroes:
        if h.heroType == heroType:
            return True
    return False


def executeTurn(curTurn, myHero):
    possibleItem = getPossibleItemToBuy(myHero)

    # TODO: once the item purchase is improved, this will run much better
    if isBehindMinion(myHero) and possibleItem: ## ## SD - shouldn't this check if we are behind the average minions? Not just that we are behind a single minion?
        # buy item IFF behind minion shield (for now at least)
        buyItem(myHero, possibleItem, curTurn)
    else:
        attackAndOrMove(myHero, curTurn)

def isBehindMinion(hero):
    minionFurthestAhead = findMinionFurthestAhead(hero.team)

    if minionFurthestAhead is None:
        return False

    if hero.team == 0:
        return hero.posX <= minionFurthestAhead.posX
    elif hero.team == 1:
        return hero.posX >= minionFurthestAhead.posX
    else:
        raise ValueError("Whose team are you on bro?!")

def getPossibleItemToBuy(myHero):
    # TODO: improve our item selection
    #if health is below 50%, buy the biggest health potion (should be the 500 health one)
    if myHero.health < (myHero.maxHealth / 2.0):
        potions = getPotions()
        potions.sort(key=lambda potion: potion.health, reverse=True)
        for potion in potions:
            if myGold >= potion.itemCost:
                return potion

    # leave space for potion
    if myHero.itemsOwned == 3:
        return None

    return getMostAffordableDamageOrMoveItem(myGold)

# Use to buy an item with damage being priority and moveSpeed taking second, this will return an itemName
# or None if neither are affordable
def getMostAffordableDamageOrMoveItem(gold):
    damageItems = [i for i in allItems if "blade" in i.itemName.lower()]
    moveSpeedItems = [i for i in allItems if "boots" in i.itemName.lower()]
    bestItem = None

    # Check for affordable items that raise damage first
    for item in damageItems:
        if (bestItem is None or item.damage > bestItem.damage) and item.itemCost <= gold:
            bestItem = item

    #TODO: I didn't use this cause it was a fall back, improving item selection will make this better
    #      We should wait for money and buy the better items later game (maybe make the choice based on turn?)

    # If no affordable items that raise damage then check for items that raise moveSpeed
    # if bestItem is None:
    #     for item in moveSpeedItems:
    #         if (bestItem is None or item.moveSpeed > bestItem.moveSpeed) and item.itemCost <= gold:
    #             bestItem = item

    return bestItem

def getPotions():
    return [item for item in allItems if item.isPotion]

def buyItem(myHero, item, curTurn):
    global myGold

    myHero.itemsOwned += 1
    myGold -=  item.itemCost
    printAction(ACTION_BUY + " " + item.itemName, curTurn)

def attackAndOrMove(myHero, curTurn):
    avgMinionXPos = getAverageMinionDistance(myTeam)
    minionFurthestAhead = findMinionFurthestAhead(myTeam)

    if minionFurthestAhead is not None:
        enemyTower = getTower(getOtherTeam(myTeam))
        desiredPosX = getFarthestXOutsideRange(enemyTower, avgMinionXPos)
        desiredPosY = minionFurthestAhead.posY
        enemyEntityToAttack = getEntityToAttack(myHero, desiredPosX, desiredPosY)

        if enemyEntityToAttack is not None:
            removeEntityIfKilled(enemyEntityToAttack, myHero)
            printMoveAttack(desiredPosX, desiredPosY, enemyEntityToAttack.unitId, curTurn)
        else:
            # Hide behind our minions
            printAction(ACTION_MOVE + " " + str(desiredPosX) + " " + str(desiredPosY), curTurn)
    else:
        # We don't have a shield minion so we should move towards our tower
        myTower = getTower(myTeam)
        printAction(ACTION_MOVE + " " + str(myTower.posX) + " " + str(myTower.posY), curTurn)

def getAverageMinionDistance(team):
    myTeamMinions = getMinions(team)
    totalMinionDistance = 0
    bufferXDistance = 75  # semi-arbitrarily chosen. played around with a few values here

    for minion in myTeamMinions:
        totalMinionDistance += minion.posX

    if len(myTeamMinions) > 1:
        avgXPos = totalMinionDistance / len(myTeamMinions)
    else: ## SD - couldn't this return a negative number if we don't have any minions or if the last minion is at an xPos < 75?
        avgXPos = totalMinionDistance - (bufferXDistance * getDirectionMultiplier(myTeam))

    return avgXPos

# Will return None if no last hits are available
def getBestPossibleLastHit(team, attackingHero, attackFromX, attackFromY):
    myDmg = attackingHero.attackDamage
    dmgThreshold = myDmg * 0.30  # TODO: temp fix for giving Hero time to get to target. If we aren't moving closer to the target this shouldn't be needed
    enemyMinionsToKill = []
    movedHero = copy.deepcopy(attackingHero) ## write a better func than this
    movedHero.posX = attackFromX
    movedHero.posY = attackFromY

    for enemyMinion in getMinions(team):
        if enemyMinion.isInRangeOf(movedHero) and enemyMinion.health <= myDmg + dmgThreshold and \
                not getTower(team).canAttack(enemyMinion.posX, enemyMinion.posY):
            enemyMinionsToKill.append(enemyMinion)
    return findClosestEntity(enemyMinionsToKill, movedHero.posX, movedHero.posY)
    #TODO: this was an old strategy for getting best last hit. It's worth trying it out again once the Hero 2 input is accounted for
    # return min(enemyMinionsToKill, key=lambda minion: minion.health) if len(enemyMinionsToKill) > 0 else None


# Takes an entity and an X value, returns the X value closest to the desired X while staying just outside the given entity's attack range
# Will return desired X or entity's X +/- attackRange depending on team of entity
def getFarthestXOutsideRange(entity, desiredX):
    if entity.team == 0:
        return max(entity.posX + (getDirectionMultiplier(entity.team) * entity.attackRange + 1), desiredX)
    else:
        return min(entity.posX + (getDirectionMultiplier(entity.team) * entity.attackRange + 1), desiredX)


# Determines which enemy entity to attack for a given turn
# Takes in the hero that is attacking, as well as the (X,Y) coordinate he will attack from
def getEntityToAttack(attackingHero, attackFromX, attackFromY):
    # Try to attack an enemy that will die with one hit so we get gold
    entityToFinishOff = getBestPossibleLastHit(getOtherTeam(myTeam), attackingHero, attackFromX, attackFromY)
    if entityToFinishOff:
        return entityToFinishOff

    # Try to last hit our own allies to prevent creep kills
    entityToFinishOff = getBestPossibleLastHit(myTeam, attackingHero, attackFromX, attackFromY)
    if entityToFinishOff:
        return entityToFinishOff

    # Try to attack an enemy hero if we deem it worthwhile
    heroToAttack = getHeroToAttack(attackingHero, attackFromX, attackFromY)
    if heroToAttack:
        return heroToAttack

    ## Find the closest defending minion to the spot we will attack from!
    defendingTeam = getOtherTeam(attackingHero.team)
    defendingMinions = getMinions(defendingTeam)
    return findClosestEntity(defendingMinions, attackFromX, attackFromY)


# Runs logic to try to attach an enemy hero. Returns the hero to attack, or None if we shouldn't
# attack any enemy heroes
def getHeroToAttack(attackingHero, attackFromX, attackFromY):
    MIN_MINION_ARMY_DIFF_TO_ATTACK_HERO = 1  # We need to have this many more minions than the enemy to attack their hero
    attackingTeam = attackingHero.team
    defendingTeam = getOtherTeam(attackingTeam)
    defendingMinions = getMinions(defendingTeam)

    ## If we aren't in range of their tower, our minion army overpowers their minion army, and they have a hero in range, attack the hero!
    if not getTower(defendingTeam).canAttack(attackFromX, attackFromY):
        defendingHero = getHero(defendingTeam)
        if defendingHero is not None and len(getMinions(attackingTeam)) - len(defendingMinions) > MIN_MINION_ARMY_DIFF_TO_ATTACK_HERO and defendingHero.isInRangeOf(attackingHero):
            return defendingHero

    # We don't want to attack a hero
    return None

def removeEntityIfKilled(enemyEntityToAttack, myHero):
    if enemyEntityToAttack.health <= myHero.attackDamage:
        allEntities.remove([e for e in allEntities if e.unitId == enemyEntityToAttack.unitId][0])


## Use to decide whether to add or subtract for the X direction
def getDirectionMultiplier(team):
    return 1 if team == 0 else -1


## Returns true if entity 1 is closer to the given team's tower than entity 2 is
## NOTE this is the X direction ONLY for now
def isCloserToTower(entity1, entity2, team):
    tower = getTower(team)
    entity1Distance = abs(getDistanceBetweenPoints(x1=tower.posX, x2=entity1.posX))
    entity2Distance = abs(getDistanceBetweenPoints(x1=tower.posX, x2=entity2.posX))

    return entity1Distance < entity2Distance


## Finds the entity farthest from the given coordinates.
def findFarthestEntity(entities, x=None, y=None):
    maxDist = None
    farthestEntity = None

    for e in entities:
        dist = getDistanceBetweenPoints(e.posX, e.posY, x, y)

        if maxDist is None or dist > maxDist:
                farthestEntity = e
                maxDist = dist

    return farthestEntity


## Finds the entity closest to the given coordinates
def findClosestEntity(entities, x=None, y=None):
    minDist = None
    closestEntity = None

    for e in entities:
        dist = getDistanceBetweenPoints(e.posX, e.posY, x, y)

        if minDist is None or dist < minDist:
                closestEntity = e
                minDist = dist

    return closestEntity


## NOTE: This is absolute value! Doesn't take direction into account at all
## If only x is provided, only takes x into account. Same thing for y
## If both x and y are provided it calculates the hypotenuse
def getDistanceBetweenPoints(x1=None, y1=None, x2=None, y2=None):
    xDist = None
    yDist = None

    if x1 is not None and x2 is not None:
        xDist = abs(x1 - x2)
    elif y1 is not None and y2 is not None:
        yDist = abs(y1 - y2)
    else:
        raise ValueError("either x or y must be provided to getDistanceBetweenPoints()")

    if xDist is not None and yDist is not None:
        return math.sqrt(xDist * xDist + yDist * yDist)
    elif xDist is not None:
        return xDist
    else:
        return yDist


## This is a bit of a misnomer because we take health into account as well
def findMinionFurthestAhead(team):
    """
    :param int team: The team for which to find a minion
    :rtype: Minion
    """
    minions = getMinions(team)
    tower = getTower(team)

    healthyMinions = [m for m in minions if not isLowHealth(m)]

    ## Look for a healthy minion first because we need a good body shield!
    ## NOTE that for now we look at the X direction ONLY when computing distance
    farthestMinion = findFarthestEntity(healthyMinions, tower.posX)
    if farthestMinion is None:
        oppositeTower = getTower(getOtherTeam(team))
        ## We don't have any healthy minions! Retreat to minion farthest from OPPOSITE tower
        farthestMinion = findFarthestEntity(minions, oppositeTower.posX)

    return farthestMinion


def isLowHealth(entity):
    if entity.maxHealth <= 0:
        return True

    lowHealthPercentage = 25
    return entity.health / entity.maxHealth < (entity.maxHealth * (lowHealthPercentage / 100))


## TODO assumes only one hero per team
def getHero(team):
    for entity in allEntities:
        if isinstance(entity, Hero) and entity.team == team:
            return entity

    # Possible that enemy hero is invisible, so none would be in the list
    # Todo: If our heroes are invisible are they also not in the list (they have to be...no way)
    return None


def getHeroes(team):
    heroes = []

    for entity in allEntities:
        if isinstance(entity, Hero) and entity.team == team:
            heroes.append(entity)

    return heroes


def getHeroByType(team, heroType):
    for entity in allEntities:
        if isinstance(entity, Hero) and entity.team == team and entity.heroType == heroType:
            return entity


def getTower(team):
    for entity in allEntities:
        if isinstance(entity, Tower) and entity.team == team:
            return entity

    raise ValueError("Missing tower for team " + `team`)


def getMinions(team):
    minions = []
    for entity in allEntities:
        if isinstance(entity, Minion) and entity.team == team:
            minions.append(entity)

    return minions


def getOtherTeam(team):
    if team == 0:
        return 1
    else:
        return 0

def readInEntities(entityCount):
    global allEntities
    allEntities = []

    for i in range(entityCount):
        # unitType: UNIT, HERO, TOWER, can also be GROOT from wood1
        # shield: useful in bronze
        # stunDuration: useful in bronze
        # countDown1: all countDown and mana variables are useful starting in bronze
        # heroType: DEADPOOL, VALKYRIE, DOCTOR_STRANGE, HULK, IRONMAN
        # isVisible: 0 if it isn't
        # itemsOwned: useful from wood1
        unitId, team, entityType, x, y, attackRange, health, maxHealth, shield, attackDamage, movementSpeed, stunDuration, goldValue, countDown1, countDown2, countDown3, mana, maxMana, manaRegeneration, heroType, isVisible, itemsOwned = raw_input().split()
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
        elif entityType == ENTITY_TYPE_GROOT:
            entity = Groot(unitId, team, x, y, attackRange, health, maxHealth, attackDamage, movementSpeed)

        if entity is None:
            raise ValueError("unknown entity type " + entityType)

        allEntities.append(entity)


def chooseHero():
    chosenHero = UNUSED_HEROES[0]
    CHOSEN_ALIVE_HEROES.append(chosenHero)
    print chosenHero
    UNUSED_HEROES.pop(0)


def unused():
    bushAndSpawnPointCount = int(raw_input())  # useful from wood1, represents the number of bushes and the number of places where neutral units can spawn
    for i in range(bushAndSpawnPointCount):
        # entityType: BUSH, from wood1 it can also be SPAWN
        entityType, x, y, radius = raw_input().split()
        x = int(x)
        y = int(y)
        radius = int(radius)

def readInItems(itemCount):
    global allItems
    allItems = []

    for i in range(itemCount):
        # itemName: contains keywords such as BRONZE, SILVER and BLADE, BOOTS connected by "" to help you sort easier
        # itemCost: BRONZE items have lowest cost, the most expensive items are LEGENDARY
        # damage: keyword BLADE is present if the most important item stat is damage
        # moveSpeed: keyword BOOTS is present if the most important item stat is moveSpeed
        # isPotion: 0 if it's not instantly consumed
        itemName, itemCost, damage, health, maxHealth, mana, maxMana, moveSpeed, manaRegeneration, isPotion = raw_input().split()
        itemCost = int(itemCost)
        damage = int(damage)
        health = int(health)
        maxHealth = int(maxHealth)
        mana = int(mana)
        maxMana = int(maxMana)
        moveSpeed = int(moveSpeed)
        manaRegeneration = int(manaRegeneration)
        isPotion = int(isPotion)

        item = Item(itemName, itemCost, damage, health, maxHealth, mana, maxMana, moveSpeed, manaRegeneration, isPotion)
        allItems.append(item)


def printMoveAttack(posX, posY, unitId, curTurn):
    printAction('{} {} {} {}'.format(ACTION_MOVE_ATTACK, posX, posY, unitId), curTurn)


def printAction(move, turn):
    global curInsult

    # update insult every 10 turns
    if turn % 10 == 0:
        curInsult = random.choice(INSULTS)

    # Write an action using print
    print move + ";" + curInsult

def debug(objOrStr):
    if isinstance(objOrStr, Entity):
        print >> sys.stderr, objOrStr.__dict__
    elif isinstance(objOrStr, Item):
        print >> sys.stderr, objOrStr.__dict__
    elif isinstance(objOrStr, list):
        debug("[")
        for el in objOrStr:
            debug(el)
        debug("]")
    else:
        print >> sys.stderr, objOrStr

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


    ## Return true if self is in range of the other entity's attack
    def isInRangeOf(self, otherEntity):
        return otherEntity.canAttack(self.posX, self.posY)


    ## Return true if given (X,Y) coordinate is in attack range of self
    def canAttack(self, posX, posY):
        dist = getDistanceBetweenPoints(self.posX, self.posY, posX, posY)
        return dist <= self.attackRange

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

class Groot(Entity):

    def __init__(self, unitId, team, posX, posY, attackRange, health, maxHealth, attackDamage, movementSpeed):
        super(Groot, self).__init__(unitId, ENTITY_TYPE_TOWER, team, posX, posY, attackRange, health, maxHealth,
                                    mana=0, maxMana=0, attackDamage=attackRange, movementSpeed=movementSpeed)

class Item(object):

    def __init__(self, itemName, itemCost, damage, health, maxHealth, mana, maxMana, moveSpeed, manaRegeneration, isPotion):
        self.itemName = itemName
        self.itemCost = itemCost
        self.damage = damage
        self.health = health
        self.maxHealth = maxHealth
        self.mana = mana
        self.maxMana = maxMana
        self.moveSpeed = moveSpeed
        self.manaRegeneration = manaRegeneration
        self.isPotion = isPotion

play()
