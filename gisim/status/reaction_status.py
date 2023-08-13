from queue import PriorityQueue
from typing import cast

from gisim.classes.enums import CharPos, ElementType, PlayerID
from gisim.classes.message import DealDamageMsg, Message, RoundEndMsg
from gisim.classes.status import CharacterStatusEntity, CombatStatusEntity
from gisim.env import INF_INT


class ElementalInfusionStatus(CharacterStatusEntity):
    """元素附魔"""

    name: str
    element: ElementType
    description: str = "Convert physical damage into elemental damage"
    value: int = 0
    active: bool = True
    remaining_usage: int = INF_INT

    def msg_handler(self, msg_queue: PriorityQueue):
        top_msg = msg_queue.queue[0]
        if self._uuid in top_msg.responded_entities:
            return False
        updated = False
        if isinstance(top_msg, DealDamageMsg):
            top_msg = cast(DealDamageMsg, top_msg)
            if top_msg.attacker == (self.player_id, self.position):
                for idx, target in enumerate(top_msg.targets):
                    if target[2] == ElementType.NONE:
                        print(
                            f"    Character Status Effect:\n        {self.name}:{self.description}\n        Origin DMG: {target[2]} -> {target[3]} + Add: 0\n        {self.player_id.name}-{self.position}\n"
                        )
                        top_msg.targets[idx] = (
                            target[0],
                            target[1],
                            self.element,
                            target[3],
                        )
                        updated = True

        if isinstance(top_msg, RoundEndMsg):
            top_msg = cast(RoundEndMsg, top_msg)
            assert (
                self.remaining_round >= 1
            ), "Remaining round should not be lower than 1!"
            self.remaining_round -= 1
            if self.remaining_round == 0:
                self.active = False
        if updated:
            top_msg.responded_entities.append(self._uuid)
        return updated


###### Status generated by elemental reactions ######


class DendroCoreStatus(CombatStatusEntity):
    """[Combat Status]When you deal Icon TCG PyroPyro DMG or Icon TCG ElectroElectro DMG to an opposing active character,
    DMG dealt +2. (1 Usage)
    """

    name: str = "Dendro Core"
    description: str = """When you deal Icon TCG PyroPyro DMG or Icon TCG ElectroElectro DMG to an opposing active character, DMG dealt +2. (1 Usage)"""
    active: bool = True
    value: int = 0
    remaining_round: int = INF_INT
    remaining_usage: int = 2

    def msg_handler(self, msg_queue: PriorityQueue) -> bool:
        top_msg = msg_queue.queue[0]
        if isinstance(top_msg, DealDamageMsg):
            top_msg = cast(DealDamageMsg, top_msg)
            attacker_id, attacker_pos = top_msg.attacker
            if attacker_id == self.player_id:
                for idx, (target_id, target_pos, element_type, dmg_val) in enumerate(
                    top_msg.targets
                ):
                    if element_type in [ElementType.PYRO, ElementType.ELECTRO]:
                        print(
                            f"    Combat Status Effect By {self.player_id.name}:\n        {self.name}:{self.description}\n        Origin DMG: {element_type.name} -> {dmg_val} + {2}\n"
                        )
                        top_msg.targets[idx] = (
                            target_id,
                            target_pos,
                            element_type,
                            dmg_val + 2,
                        )
                    self.remaining_usage -= 1

        if self.remaining_usage == 0 or self.remaining_round == 0:
            self.active = False

        return False


class CatalyzingFieldStatus(CombatStatusEntity):
    """[Combat Status]When you deal Icon TCG ElectroElectro DMG or Icon TCG DendroDendro DMG to an opposing active character,
    DMG dealt +1. (3 Usages)"""

    name: str = "Catalyzing Field"
    description: str = """When you deal Icon TCG ElectroElectro DMG or Icon TCG DendroDendro DMG to an opposing active character, DMG dealt +1. (2 Usages)"""
    active: bool = True
    value: int = 0
    remaining_round: int = INF_INT
    remaining_usage: int = 3

    def msg_handler(self, msg_queue: PriorityQueue) -> bool:
        top_msg = msg_queue.queue[0]
        if isinstance(top_msg, DealDamageMsg):
            top_msg = cast(DealDamageMsg, top_msg)
            attacker_id, attacker_pos = top_msg.attacker
            if attacker_id == self.player_id:
                for idx, (target_id, target_pos, element_type, dmg_val) in enumerate(
                    top_msg.targets
                ):
                    if element_type in [ElementType.DENDRO, ElementType.ELECTRO]:
                        print(
                            f"    Combat Status Effect By {self.player_id.name}:\n        {self.name}:{self.description}\n        Origin DMG: {element_type.name} -> {dmg_val} + {2}\n"
                        )
                        top_msg.targets[idx] = (
                            target_id,
                            target_pos,
                            element_type,
                            dmg_val + 1,
                        )
                    self.remaining_usage -= 1

            if self.remaining_usage == 0 or self.remaining_round == 0:
                self.active = False

            return False


class FrozenEffectStatus(CharacterStatusEntity):
    """
    [Character Status]the target is unable to perform any Actions this round
    (Can be removed in advance after the target receives Physical or Pyro DMG,
    in which case they will take +2 DMG)
    """

    name: str = "Frozen Effect"
    element: ElementType = ElementType.NONE
    description: str = """[Character Status]the target is unable to perform any Actions this round(Can be removed in advance after the target receives Physical or Pyro DMG, in which case they will take +2 DMG)"""
    value: int = 0
    active: bool = True
    remaining_usage = 1

    def msg_handler(self, msg_queue: PriorityQueue):
        top_msg = msg_queue.queue[0]
        updated = False
        if self._uuid in top_msg.responded_entities:
            return False

        if isinstance(top_msg, DealDamageMsg):
            top_msg = cast(DealDamageMsg, top_msg)
            if top_msg.damage_calculation_ended:
                return False
            for idx, (target_id, target_pos, element_type, dmg_val) in enumerate(
                top_msg.targets
            ):
                if (
                    target_id == self.player_id
                    and target_pos == self.position
                    and element_type in [ElementType.NONE, ElementType.PYRO]
                ):
                    print(
                        f"    Character Status Effect:\n        {self.name}:{self.description}\n        Origin DMG: {element_type.name} -> {dmg_val} + Add: 2\n        {self.player_id.name}-{self.position}\n"
                    )

                    top_msg.targets[idx] = (
                        target_id,
                        target_pos,
                        element_type,
                        dmg_val + 2,
                    )
                    updated = True
                    self.remaining_usage -= 1

        if isinstance(top_msg, RoundEndMsg):
            self.remaining_round -= 1
            if self.remaining_round == 0:
                self.active = False

        if updated:
            top_msg.responded_entities.append(self._uuid)
        return updated


class ShieldStatus(CombatStatusEntity):
    """Shield"""

    name: str = "Shield"
    description: str = "Shield"
    active: bool = True
    value: int
    remaining_round: int = INF_INT
    remaining_usage: int = 1

    def msg_handler(self, msg_queue: PriorityQueue):
        top_msg = msg_queue.queue[0]
        updated = False

        if self._uuid in top_msg.responded_entities:
            return False

        if isinstance(top_msg, DealDamageMsg):
            top_msg = cast(DealDamageMsg, top_msg)

            for idx, (target_id, target_pos, element_type, dmg_val) in enumerate(
                top_msg.targets
            ):
                if target_id == self.player_id and dmg_val > 0:
                    print(
                        f"    Combat Status Effect By {self.player_id.name}:\n        {self.name}:{self.description}\n        Origin DMG: {element_type.name} -> {dmg_val} - {1}\n"
                    )
                    after_dmg = max(0, dmg_val - self.value)
                    # 护盾只能抵消伤害，改挂元素还是得挂元素

                    top_msg.targets[idx] = (
                        target_id,
                        target_pos,
                        element_type,
                        after_dmg,
                    )
                    self.value = max(0, self.value - dmg_val)
                    if self.value == 0:
                        self.remaining_usage = 0
                    updated = True

        if self.remaining_usage == 0:
            self.active = False
        if updated:
            top_msg.responded_entities.append(self._uuid)

        return updated