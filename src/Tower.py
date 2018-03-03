import Entity

class Tower(Entity):

    def __init__(self, unitId, team, posX, posY):
        super(Tower, self).__init__(unitId, type="TOWER", team=team, attackRange=400, health=3000, maxHealth=3000,
                                    mana=0, maxMana=0, attackDamage=100, movementSpeed=0, posX=posX, posY=posY)



