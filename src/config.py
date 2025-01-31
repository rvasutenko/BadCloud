from dataclasses import dataclass

@dataclass
class Config:
    token: str = 'BOT_TOKEN'
    admin_ids: int = 1
    pay_token: str = '1744374395:TEST:01a3edba2453ddf525bd'
    token_p2p: str = 'P2P_TOKEN'
