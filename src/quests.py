from pygame import Rect, Surface, display
from fonts import TITLE_FONT, TEXT_FONT, auto_wrap
from items import IronIngot, GoldIngot
from blocks import Sorter, Trash, FloorBlock, Connecter
import colors

class Quest:
    def __init__(self, game, title: str, description: str= "") -> None:
        from _main import Game

        self.game: Game= game
        self.title = title
        self.description = description
        self.done= False
        self.pourcentage_done= 0
        pass
    def update_pourcentage(self):
        pass
    def check_success(self) -> bool:
        """ Renvoie si oui ou non (`True` ou `False`) le joueur a accomplis cette quête
        """
        return False
    def give_reward(self) -> None:
        """ Done la récompense au joueur
        """
        return
    def draw(self):
        card_padding= 10
        progress_bar_height= 5
        card_width = 250
        win_w, win_h= display.get_window_size()

        # title
        title_text, title_rect= TITLE_FONT.render(self.title, colors.orange)
        # caption
        caption_text, caption_rect= auto_wrap(TEXT_FONT, TEXT_FONT.size, self.description, card_width, "right", (255, 255, 255))

        card_w, card_h= (
            card_width + card_padding *2,
            title_rect.height + caption_rect.height + card_padding *4 + progress_bar_height
        )
        card_rect = Rect(
            win_w - card_w, (win_h - card_h)/2,
            card_w, card_h
        )
        card = Surface(card_rect.size)

        card.blit(title_text, (card_padding, card_padding))
        card.blit(caption_text, (
            card_rect.width - caption_rect.width - card_padding,
            card_rect.height - caption_rect.height - 2*card_padding - progress_bar_height
        ))

        progress_bar = Surface((card_rect.width - 2* card_padding, progress_bar_height)).convert_alpha()
        progress_bar_bg = colors.yellow
        progress_bar_bg.a = 255 // 5
        progress_bar.fill(progress_bar_bg)

        progress = Surface((progress_bar.get_rect().width * self.pourcentage_done / 100, progress_bar_height))
        progress.fill(colors.green)
        progress_bar.blit(progress, (0, 0))

        card.blit(progress_bar, (card_padding, card_rect.height - card_padding - progress_bar_height))
        self.game.draw(card, card_rect.topleft)

# Quest are set in order of their definition (First defined = First item in the AllTheQuest list)

class FirstSelledItem(Quest):
    def __init__(self, game) -> None:
        super().__init__(game, "Your first quest", "Sell an item with the help of a query and a seller.")
    def check_success(self) -> bool:
        return len(self.game.player.selled) > 0
    def give_reward(self) -> None:
        return self.game.player.gain(20)

class Achieve150Credits(Quest):
    def __init__(self, game) -> None:
        super().__init__(game, "Making money", "Make 150 credits from now.")
        self.init_credit= self.game.player.balance
    def check_success(self) -> bool:
        return self.game.player.balance - self.init_credit > 150
    def give_reward(self) -> None:
        self.game.player.inventory_bar.content+= [(Trash(self.game), 20), (Sorter(self.game), 5)]
        return self.game.player.gain(100)
    def update_pourcentage(self):
        self.pourcentage_done= ((self.game.player.balance - self.init_credit) / 150) *100

class Sell20IronsInARow(Quest):
    def __init__(self, game) -> None:
        super().__init__(game, "Only Irons", "Sell 20 iron ingots in a row.")
    def check_success(self) -> bool:
        last_20_selled_items = self.game.player.selled[len(self.game.player.selled) - 20:]
        for item in last_20_selled_items:
            if not type(item) == IronIngot:
                return False
        return True
    def update_pourcentage(self):
        last_20_selled_items = self.game.player.selled[len(self.game.player.selled) - 20:]
        valid= 0
        for item in reversed(last_20_selled_items):
            if type(item) == IronIngot:
                valid+= 1
            else: break
        self.pourcentage_done = (valid / 20) * 100
    def give_reward(self) -> None:
        return self.game.player.gain(120)

class ABitHarder(Quest):
    def __init__(self, game) -> None:
        super().__init__(game, "A bit harder", "Sell 7 gold ingots in a row, with only 4 blocks.")
        self.checking_from_index = 0
        self.reset_index()
    def check_success(self) -> bool:
        placed_blocks = self.game.map.filter_blocks(lambda block: not isinstance(block, FloorBlock))
        if len(placed_blocks) != 4: return False
        
        last_selled_items = self.game.player.selled[self.checking_from_index:]
        if len(last_selled_items) < 7: return False

        for item in last_selled_items:
            if type(item) != GoldIngot:
                return False
        return True
    def update_pourcentage(self):
        placed_blocks = self.game.map.filter_blocks(lambda block: not isinstance(block, FloorBlock))
        if len(placed_blocks) != 4:
            self.pourcentage_done = 0
            return self.reset_index()
        
        last_selled_items = self.game.player.selled[self.checking_from_index:]
        for item in reversed(last_selled_items):
            if type(item) != GoldIngot:
                self.pourcentage_done = 0
                return self.reset_index()
        
        self.pourcentage_done = (len(last_selled_items) / 7) * 100
    def reset_index(self):
        self.checking_from_index = len(self.game.player.selled) -1
    def give_reward(self) -> None:
        self.game.player.inventory_bar.content.append((Connecter(self.game), 5))

class LovingMoney(Quest):
    def __init__(self, game) -> None:
        super().__init__(game, "We all love money...", "Achieve 5000 credits. (We recommend you to make a big factory)")
    def check_success(self) -> bool:
        return self.game.player.balance >= 5000
    def update_pourcentage(self):
        self.pourcentage_done = (self.game.player.balance / 5000) * 100
    def give_reward(self) -> None:
        return super().give_reward()

class Finished(Quest):
    def __init__(self, game) -> None:
        super().__init__(game, "Great Job!", "You've finished all the quests! Now have fun playing and chilling at our game.")

AllTheQuests: list[type[Quest]] = []
for QuestType in vars().copy().values():
    if type(QuestType) == type(Quest) and issubclass(QuestType, Quest) and QuestType != Quest:
        AllTheQuests.append(QuestType)