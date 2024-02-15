from glob import glob
import logging
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from ue5config import UE5Config

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

param_lookup = {
    "DayTimeSpeedRate": {"env": "DAYTIME_SPEEDRATE", "description": "Day time speed", "visible": True, "default": 1.0},
    "NightTimeSpeedRate": {"env": "NIGHTTIME_SPEEDRATE", "description": "Night time speed", "visible": True, "default": 1.0},
    "ExpRate": {"env": "EXP_RATE", "description": "EXP rate", "visible": True, "default": 1.0},
    "PalCaptureRate": {"env": "PAL_CAPTURE_RATE", "description": "Pal capture rate", "visible": True, "default": 1.0},
    "PalSpawnNumRate": {"env": "PAL_SPAWN_NUM_RATE", "description": "Pal Appearance Rate", "visible": True, "default": 1.0},
    "PalDamageRateAttack": {"env": "PAL_DAMAGE_RATE_ATTACK", "description": "Damage from Pals Multiplier", "visible": True, "default": 1.0},
    "PalDamageRateDefense": {"env": "PAL_DAMAGE_RATE_DEFENSE", "description": "Damage to Pals Multiplier", "visible": True, "default": 1.0},
    "PlayerDamageRateAttack": {"env": "PLAYER_DAMAGE_RATE_ATTACK", "description": "Damage from Player Multiplier", "visible": True, "default": 1.0},
    "PlayerDamageRateDefense": {"env": "PLAYER_DAMAGE_RATE_DEFENSE", "description": "Damage to Player Multiplier", "visible": True, "default": 1.0},
    "PlayerStomachDecreaceRate": {"env": "PLAYER_STOMACH_DECREASE_RATE", "description": "Player Hunger Depletion Rate", "visible": True, "default": 1.0},
    "PlayerStaminaDecreaceRate": {"env": "PLAYER_STAMINA_DECREASE_RATE", "description": "Player Stamina Reduction Rate", "visible": True, "default": 1.0},
    "PlayerAutoHPRegeneRate": {"env": "PLAYER_AUTO_HP_REGEN_RATE", "description": "Player Auto Health Regeneration Rate", "visible": True, "default": 1.0},
    "PlayerAutoHpRegeneRateInSleep": {"env": "PLAYER_AUTO_HP_REGEN_RATE_IN_SLEEP", "description": "Player Sleep Health Regeneration Rate", "visible": True, "default": 1.0},
    "PalStomachDecreaceRate": {"env": "PAL_STOMACH_DECREASE_RATE", "description": "Pal Hunger Depletion Rate", "visible": True, "default": 1.0},
    "PalStaminaDecreaceRate": {"env": "PAL_STAMINA_DECREASE_RATE", "description": "Pal Stamina Reduction Rate", "visible": True, "default": 1.0},
    "PalAutoHPRegeneRate": {"env": "PAL_AUTO_HP_REGEN_RATE", "description": "Pal Auto Health Regeneration Rate", "visible": True, "default": 1.0},
    "PalAutoHpRegeneRateInSleep": {"env": "PAL_AUTO_HP_REGEN_RATE_IN_SLEEP", "description": "Pal Sleep Health Regeneration Rate (Health Regeneration Rate in Palbox)", "visible": True, "default": 1.0},
    "BuildObjectDamageRate": {"env": "BUILD_OBJECT_DAMAGE_RATE", "description": "Damage to Structure Multiplier", "visible": True, "default": 1.0},
    "BuildObjectDeteriorationDamageRate": {"env": "BUILD_OBJECT_DETERIORATION_DAMAGE_RATE", "description": "Structure Deterioration Rate", "visible": True, "default": 1.0},
    "CollectionDropRate": {"env": "COLLECTION_DROP_RATE", "description": "Gatherable Items Multiplier", "visible": True, "default": 1.0},
    "CollectionObjectHpRate": {"env": "COLLECTION_OBJECT_HP_RATE", "description": "Gatherable Objects Health Multiplier", "visible": True, "default": 1.0},
    "CollectionObjectRespawnSpeedRate": {"env": "COLLECTION_OBJECT_RESPAWN_SPEED_RATE", "description": "Gatherable Objects Respawn Interval", "visible": True, "default": 1.0},
    "EnemyDropItemRate": {"env": "ENEMY_DROP_ITEM_RATE", "description": "Dropped Items Multiplier", "visible": True, "default": 1.0},
    "DeathPenalty": {"env": "DEATH_PENALTY", "description": "Death Penalty", "visible": True, "default": "All"},
    "bEnableInvaderEnemy": {"env": "ENABLE_INVADER_ENEMY", "description": "Enable Invader", "visible": True, "default": True},
    "GuildPlayerMaxNum": {"env": "GUILD_PLAYER_MAX_NUM", "description": "Max Player Number of Guilds", "visible": True, "default": 20},
    "PalEggDefaultHatchingTime": {"env": "PAL_EGG_DEFAULT_HATCHING_TIME", "description": "Incubation Time (hours)", "visible": True, "default": 72.0},
    "ServerPlayerMaxNum": {"env": "SERVER_PLAYER_MAX_NUM", "description": "Maximum number of players that can join the server", "visible": True, "default": 32},
    "Difficulty": {"env": "DIFFICULTY", "description": "Game Difficulty", "visible": True, "default": None}, # Hidden because defaults to nothing.. The other settings sort of determine difficulty
    "bEnablePlayerToPlayerDamage": {"env": "ENABLE_PLAYER_TO_PLAYER_DAMAGE", "description": "Player to player damage", "visible": True, "default": False},
    "bEnableFriendlyFire": {"env": "ENABLE_FRIENDLY_FIRE", "description": "Friendly fire", "visible": True, "default": False},
    "bEnableAimAssistPad": {"env": "ENABLE_AIM_ASSIST_PAD", "description": "Controller aim assist", "visible": True, "default": True},
    "bEnableAimAssistKeyboard": {"env": "ENABLE_AIM_ASSIST_KEYBOARD", "description": "Keyboard aim assist", "visible": True, "default": False},
    "DropItemMaxNum": {"env": "DROP_ITEM_MAX_NUM", "description": "Item drop world max", "visible": True, "default": 3000},
    "DropItemMaxNum_UNKO": {"env": "DROP_ITEM_MAX_NUM_UNKO", "description": "UNKO Item drop world max", "visible": True, "default": 100},
    "BaseCampMaxNum": {"env": "BASE_CAMP_MAX_NUM", "description": "Max number of base camps", "visible": True, "default": 128},
    "BaseCampWorkerMaxNum": {"env": "BASE_CAMP_WORKER_MAX_NUM", "description": "Max number of base camp workers", "visible": True, "default": 15},
    "DropItemAliveMaxHours": {"env": "DROP_ITEM_ALIVE_MAX_HOURS", "description": "Time for dropped items to despawn", "visible": True, "default": 1.0},
    "bAutoResetGuildNoOnlinePlayers": {"env": "AUTO_RESET_GUILD_NO_ONLINE_PLAYERS", "description": "Guilds reset when no online players", "visible": True, "default": False},
    "AutoResetGuildTimeNoOnlinePlayers": {"env": "AUTO_RESET_GUILD_TIME_NO_ONLINE_PLAYERS", "description": "Time for guild reset when no online players (hours)", "visible": True, "default": 72.0},
    "WorkSpeedRate": {"env": "WORK_SPEED_RATE", "description": "Work speed multiplier", "visible": True, "default": 1.0},
    "bIsPvP": {"env": "IS_PVP", "description": "Enable Player-vs-Player (PvP)", "visible": True, "default": False},
    "bCanPickupOtherGuildDeathPenaltyDrop": {"env": "CAN_PICKUP_OTHER_GUILD_DEATH_PENALTY_DROP", "description": "Allow players from other guilds to pick up deaht penalty items", "visible": True, "default": False},
    "bEnableNonLoginPenalty": {"env": "ENABLE_NON_LOGIN_PENALTY", "description": "Non-login penalty", "visible": True, "default": True},
    "bEnableFastTravel": {"env": "ENABLE_FAST_TRAVEL", "description": "Fast traveling", "visible": True, "default": True},
    "bIsStartLocationSelectByMap": {"env": "IS_START_LOCATION_SELECT_BY_MAP", "description": "Select starting location", "visible": True, "default": True},
    "bExistPlayerAfterLogout": {"env": "EXIST_PLAYER_AFTER_LOGOUT", "description": "Delete players after logout", "visible": True, "default": False},
    "bEnableDefenseOtherGuildPlayer": {"env": "ENABLE_DEFENSE_OTHER_GUILD_PLAYER", "description": "Defense against other guild players", "visible": True, "default": False},
    "CoopPlayerMaxNum": {"env": "COOP_PLAYER_MAX_NUM", "description": "Max number of guild members", "visible": True, "default": 4}}

templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def hello_world(request: Request):
    palworld_dir = os.getenv("PALWORLD_DIR")
    if not palworld_dir:
        logging.error("PALWORLD_DIR must be set")
        return HTMLResponse("PALWORLD_DIR must not set")

    settings_file = glob(f"{palworld_dir}/**/PalWorldSettings.ini", recursive=True)
    if len(settings_file) == 0:
        logging.error(f"No PalWorldSettings.ini found in {palworld_dir}")
        return HTMLResponse("Unable to find PalWorldSettings.ini")
    if len(settings_file) > 1:
        logging.error(f"Multiple PalWorldSettings.ini found in {palworld_dir}. Use more specific directory.")
        return HTMLResponse("Unable to find PalWorldSettings.ini")

    server_files = Path(settings_file[0])
    cfg = UE5Config()
    cfg.read_file(server_files)
    settings = cfg.get('/Script/Pal.PalGameWorldSettings')

    changed = []
    vanilla = []
    for key, value in settings["OptionSettings"].items():
        param = param_lookup.get(key)
        if not param:
            # Property is not being tracked
            continue

        hidden = os.getenv(param.get("env"), "show")
        if hidden.lower() == "hide-always":
            # The property should be hidden
            continue

        if value != param.get("default"):
            # The property was configured differently
            changed.append(dict(param, new_value=value, property=key))
        elif hidden.lower() != "hide-default":
            # The property is not different than default
            vanilla.append(dict(param, property=key))
    
    # Extract server name and description separately
    server_name = settings["OptionSettings"]["ServerName"]
    server_desc = settings["OptionSettings"]["ServerDescription"]
    
    return templates.TemplateResponse(
        request=request, name="index.html", context={"changed": changed, "vanilla": vanilla, "server_name": server_name, "server_desc": server_desc}
    )
