"""Exercise the real gossip selection body against a minimal core stub."""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class SelectionTest(unittest.TestCase):
    def test_selection(self):
        guard = Path('/home/aaron/Documents/ChatGPT/wow private server/scripts/wow-build-host-guard')
        subprocess.run([str(guard)], check=True)
        text = (ROOT / 'src/instance_reset.cpp').read_text()
        start = text.index('bool InstanceReset::OnGossipSelect(')
        end = text.index('\nvoid InstanceResetWorldConfig::', start)
        header = (ROOT / 'src/instance_reset.h').read_text()
        declaration = next(line for line in header.splitlines() if 'transactionType = 0;' in line)
        stub = r'''
#include <cstdint>
#include <map>
#include <string>
using uint8=uint8_t; using uint16=uint16_t; using uint32=uint32_t;
constexpr int GOSSIP_ACTION_INFO_DEF=100, MAX_DIFFICULTY=4, LANG_UNIVERSAL=0;
enum { LOCALE_enUS, LOCALE_koKR, LOCALE_frFR, LOCALE_deDE, LOCALE_zhCN, LOCALE_zhTW, LOCALE_esES, LOCALE_esMX, LOCALE_ruRU };
using Difficulty=int; using BoundInstancesMap=std::map<int,int>;
bool enable=true; uint16 count=2; uint32 token=42, money=100;
''' + declaration + r'''
struct Session { int GetSessionDbLocaleIndex(){return LOCALE_enUS;} };
struct Player { bool hasToken=true; uint32 balance=100; int chargedToken=0, chargedMoney=0; Session session;
 bool HasItemCount(uint32,uint16,bool){return hasToken;} uint32 GetMoney(){return balance;}
 int GetGUID(){return 1;} int GetMapId(){return 999;} Session* GetSession(){return &session;}
 void DestroyItemCount(uint32,uint16,bool){++chargedToken;} void ModifyMoney(int32_t n){chargedMoney += n;}
};
struct Creature { void Whisper(std::string,int,Player*){} };
struct Config { template<class T> T GetOption(char const*,T fallback){return fallback;} } config;
Config* sConfigMgr=&config;
struct SaveMgr { BoundInstancesMap bound{{1,1}}; int resets=0;
 BoundInstancesMap const& PlayerGetBoundInstances(int,Difficulty){return bound;}
 void PlayerUnbindInstance(int,int,Difficulty,bool,Player*){++resets;bound.clear();}
} saves; SaveMgr* sInstanceSaveMgr=&saves;
void ClearGossipMenuFor(Player*){} void CloseGossipMenuFor(Player*){}
struct InstanceReset { bool OnGossipSelect(Player*,Creature*,uint32,uint32); };
''' + text[start:end] + r'''
int main(){
 InstanceReset npc; Creature creature;
 auto check=[&](uint32 type,bool enabled,bool tokens,uint32 balance,int resets,int chargedToken,int chargedMoney){
  Player p; p.hasToken=tokens; p.balance=balance; enable=enabled; transactionType=type; saves.bound={{1,1}}; saves.resets=0;
  npc.OnGossipSelect(&p,&creature,0,GOSSIP_ACTION_INFO_DEF+1);
  return saves.resets==resets && p.chargedToken==chargedToken && p.chargedMoney==chargedMoney;
 };
 if(!check(0,true,false,0,1,0,0)) return 1;
 if(!check(0,false,true,100,0,0,0)) return 2;
 if(!check(256,true,true,100,0,0,0)) return 3;
 if(!check(1,true,false,100,0,0,0)) return 4;
 if(!check(2,true,true,99,0,0,0)) return 5;
 if(!check(3,true,false,100,0,0,0)) return 6;
 if(!check(3,true,true,99,0,0,0)) return 7;
 if(!check(1,true,true,100,1,1,0)) return 8;
 if(!check(2,true,true,100,1,0,-100)) return 9;
 if(!check(3,true,true,100,1,1,-100)) return 10;
 return 0;
}
'''
        with tempfile.TemporaryDirectory() as directory:
            cpp = Path(directory) / 'selection.cpp'
            cpp.write_text(stub)
            binary = Path(directory) / 'selection'
            subprocess.run(['g++', '-std=c++17', str(cpp), '-o', str(binary)], check=True)
            subprocess.run([str(binary)], check=True)

if __name__ == '__main__':
    unittest.main()
