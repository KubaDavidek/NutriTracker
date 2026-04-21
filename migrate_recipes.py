"""
migrate_recipes.py – Vytvoří tabulku recipes a naplní ji daty.

Spuštění:
    python migrate_recipes.py

Skript je idempotentní – tabulku vytvoří jen pokud neexistuje,
a recepty vloží jen pokud tabulka je prázdná.
"""

import json
import os
import sys

import psycopg2
from dotenv import load_dotenv

load_dotenv()

# ── Nové recepty (přidány navíc k stávajícím) ─────────────────────────────────
NEW_RECIPES = [
    {
        "name":        "Špagety s celozrnnou těstovinou a boloňskou omáčkou",
        "kcal":        460,
        "protein":     30,
        "carbs":       52,
        "fat":         12,
        "time":        "35 min",
        "servings":    3,
        "category":    "Hlavní jídla",
        "tags":        ["klasika", "proteinové", "příprava do zásoby"],
        "ingredients": [
            "300 g celozrnných špaget",
            "300 g mletého hovězího (nebo mix hovězí+vepřové)",
            "400 g rajčat pelati",
            "1 cibule",
            "2 stroužky česneku",
            "1 mrkev",
            "1 stonku celeru",
            "sklenička červeného vína (volitelně)",
            "olivový olej, oregano, bazalka, sůl, pepř",
        ],
        "instructions": (
            "1. Cibuli, mrkev a celer nakrájej nadrobno. V hlubší pánvi rozehřej olej a osmahni zeleninu 5 minut.\n"
            "2. Přidej prolisovaný česnek, míchej 1 minutu.\n"
            "3. Přidej mleté maso a za stálého míchání ho rozdrob a opékej, dokud není celé opečené (7–8 min).\n"
            "4. Přilij víno (pokud používáš) a nechej vypařit 2 minuty.\n"
            "5. Přidej pelati rozmačkané rukou, oregano, bazalku, sůl a pepř.\n"
            "6. Vař na mírném plameni odkryté 20 minut – omáčka zhoustne a chutě se propojí.\n"
            "7. Těstoviny uvař dle obalu v osolené vodě al dente. Sceď a zamíchej přímo do omáčky.\n"
            "8. Podávej s nastrouhaným parmazánem."
        ),
        "tip": "Přidání zeleniny (mrkev, celer) do bolognese je klasický italský základ – soffritto.",
    },
    {
        "name":        "Kuřecí souvlaki s tzatziki a pitou",
        "kcal":        430,
        "protein":     36,
        "carbs":       38,
        "fat":         14,
        "time":        "30 min (+ 1 hod marinování)",
        "servings":    2,
        "category":    "Hlavní jídla",
        "tags":        ["proteinové", "středomořské", "grilované"],
        "ingredients": [
            "400 g kuřecích prsou",
            "2 pita chleby",
            "200 g řeckého jogurtu",
            "1 okurka",
            "2 stroužky česneku",
            "citron, olivový olej",
            "oregano, kmín, paprika, sůl, pepř",
            "cherry rajčata, červená cibule na podávání",
        ],
        "instructions": (
            "1. Kuře nakrájej na kostky 3×3 cm. Marinuj v oleji, citronové šťávě, prolisovaném česneku, oreganu, paprice, soli a pepři – min. 1 hodinu.\n"
            "2. Tzatziki: okurku nastrouhej na hrubém struhadle, vymačkej přes utěrku co nejvíce vody. Smíchej s jogurtem, prolisovaným česnekem, solí a trochou olivového oleje.\n"
            "3. Kuřecí kostky nauč na špejle a griluj nebo opékej na pánvi 3–4 minuty z každé strany.\n"
            "4. Pity lehce prohřej v troubě nebo na suché pánvi.\n"
            "5. Na pitu rozlož tzatziki, přidej kuře ze špejle, cherry rajčata a červenou cibuli nakrájenou na kolečka.\n"
            "6. Zaroluj nebo podávej otevřené."
        ),
        "tip": "Marinování v citronu zjemňuje maso a pomáhá ho zkřehčit.",
    },
    {
        "name":        "Losos teriyaki s rýží a brokolicí",
        "kcal":        480,
        "protein":     38,
        "carbs":       45,
        "fat":         14,
        "time":        "25 min",
        "servings":    2,
        "category":    "Hlavní jídla",
        "tags":        ["bez lepku", "omega-3", "asijské"],
        "ingredients": [
            "2× filet lososa (150 g)",
            "200 g jasmínové nebo hnědé rýže",
            "300 g brokolice",
            "3 lžíce sójové omáčky",
            "1 lžíce medu",
            "1 lžičce sezamového oleje",
            "1 stroužek česneku, zázvor",
            "sesam na posypání",
        ],
        "instructions": (
            "1. Teriyaki omáčka: smíchej sójovou omáčku, med, sezamový olej, prolisovaný česnek a nastrouhaný zázvor.\n"
            "2. Lososové filety potři polovinou omáčky a nechej 10 minut marinovat.\n"
            "3. Rýži uvař dle pokynů na obalu.\n"
            "4. Brokolici rozeber, blanšíruj 3 minuty v osolené vodě a sceď.\n"
            "5. Pánev rozehřej na středním plameni, přidej trochu oleje. Lososa peč 3–4 minuty kůží dolů, pak otoč a peč dalších 2–3 minuty.\n"
            "6. Posledních 30 sekund přilij zbytek omáčky a nechej zkaramelizovat.\n"
            "7. Podávej na rýži s brokolicí, posyp sesamem."
        ),
        "tip": "Teriyaki omáčka z medu a sóji je zdravější alternativa k hotovým sladkým omáčkám.",
    },
    {
        "name":        "Zapečené brambory se zakysanou smetanou a bylinkami",
        "kcal":        310,
        "protein":     8,
        "carbs":       52,
        "fat":         8,
        "time":        "55 min",
        "servings":    2,
        "category":    "Hlavní jídla",
        "tags":        ["vegetariánské", "bez lepku", "česká klasika"],
        "ingredients": [
            "4 střední brambory",
            "150 g zakysané smetany (light)",
            "50 g tvrdého sýra",
            "pažitka, pažitek, sůl, pepř",
            "olivový olej",
        ],
        "instructions": (
            "1. Troubu předehřej na 200 °C.\n"
            "2. Brambory propíchej vidličkou a potři olivovým olejem a solí.\n"
            "3. Peč přímo na roštu 45–50 minut dokud nejsou měkké celé (zkontroluj špejlí).\n"
            "4. Vyndej, řízni křížem navrch a roztlač trochu dužinu.\n"
            "5. Přidej zakysanou smetanu, nastrouhaný sýr a posyp pažitkou.\n"
            "6. Vrátil do trouby na 5 minut, dokud sýr nezačne táhnout.\n"
            "7. Podávej s čerstvou pažitkou a pepřem."
        ),
        "tip": "Pečené brambory v slupce zachovávají draslík lépe než vařené.",
    },
    {
        "name":        "Francouzský toast s ricottou a jahodami",
        "kcal":        360,
        "protein":     18,
        "carbs":       44,
        "fat":         12,
        "time":        "15 min",
        "servings":    2,
        "category":    "Snídaně",
        "tags":        ["proteinové", "sladká snídaně", "vegetariánské"],
        "ingredients": [
            "4 plátky celozrnného chleba",
            "2 vejce",
            "100 ml mléka",
            "150 g ricotty",
            "200 g čerstvých jahod",
            "1 lžíce medu nebo javorového sirupu",
            "špetka skořice, vanilka",
        ],
        "instructions": (
            "1. Vejce rozšlehej s mlékem, skořicí a vanilkou v mělkém talíři.\n"
            "2. Plátky chleba namočit v příchutί směsi z obou stran (30 sekund na každé straně).\n"
            "3. Na středním plameni rozehřej pánev s trochou másla nebo kokosového oleje.\n"
            "4. Opékej plátky 2–3 minuty z každé strany do zlatohněda.\n"
            "5. Jahody nakrájej na čtvrtiny, smíchej s lžičkou medu.\n"
            "6. Na každý toast přidej ricottu a jahodovou směs.\n"
            "7. Pokapal medem nebo sirupem a podávej ihned."
        ),
        "tip": "Ricotta má méně tuku než tvarohový krém a je bohatá na vápník.",
    },
    {
        "name":        "Kuřecí nudlová polévka s miso",
        "kcal":        240,
        "protein":     18,
        "carbs":       28,
        "fat":         5,
        "time":        "25 min",
        "servings":    3,
        "category":    "Polévky",
        "tags":        ["asijské", "lehce stravitelné", "probiotika"],
        "ingredients": [
            "200 g kuřecích prsou",
            "100 g rýžových nudlí",
            "2 lžíce bílé miso pasty",
            "800 ml kuřecího vývaru",
            "2 cm zázvoru",
            "2 stroužky česneku",
            "jarní cibulka, sójová omáčka",
            "baby špenát nebo bok choy",
        ],
        "instructions": (
            "1. Vývar přiveď k varu. Přidej plátky zázvoru a prolisovaný česnek, vař 5 minut.\n"
            "2. Kuřecí prsa přidej do vývaru a vař 12–15 minut na mírném plameni. Vyndej a roztrhej na proužky vidličkou.\n"
            "3. Nudle uvař dle pokynů (obvykle 3–5 min v horké vodě), sceď a opláchni studenou vodou.\n"
            "4. Miso pastu rozmíchej v hrnku s trochou horkého vývaru (nesmí se vařit – ztratí probiotika). Přimíchej do polévky.\n"
            "5. Přidej kuřecí proužky a špenát, nechej 1 minutu prohřát.\n"
            "6. Do misek dej nudle, přelij polévkou.\n"
            "7. Ozdobí nakrájenou jarní cibulkou a kapkou sójové omáčky."
        ),
        "tip": "Miso nepřivádět k varu – zničíš prospěšné bakterie.",
    },
    {
        "name":        "Krémová dýňová polévka",
        "kcal":        175,
        "protein":     4,
        "carbs":       28,
        "fat":         6,
        "time":        "35 min",
        "servings":    4,
        "category":    "Polévky",
        "tags":        ["vegan", "bez lepku", "podzimní"],
        "ingredients": [
            "800 g dýně Hokkaido (nebo Butternut)",
            "1 cibule",
            "2 stroužky česneku",
            "600 ml zeleninového vývaru",
            "100 ml kokosového mléka",
            "1 lžíce olivového oleje",
            "muškátový oříšek, zázvor, sůl, pepř",
            "dýňová semínka na posypání",
        ],
        "instructions": (
            "1. Dýni překroj, vydlabej semínka a nakrájej na kostky (Hokkaido nemusíš loupat).\n"
            "2. Na oleji osmahni nakrájenou cibuli 3 minuty, přidej česnek a nastrouhaný zázvor, míchej 1 minutu.\n"
            "3. Přidej dýni a zalijte vývar. Vař 20 minut dokud dýně nezměkne.\n"
            "4. Rozmixuj tyčovým mixérem do hladkého krému.\n"
            "5. Přilij kokosové mléko, prohřej. Dochucuj solí, pepřem a muškátovým oříškem.\n"
            "6. Podávej s kapkou kokosového mléka, opraženými dýňovými semínky a čerstvým chlebem."
        ),
        "tip": "Dýně Hokkaido se dá péct i se slupkou – obsahuje více živin než dužina.",
    },
    {
        "name":        "Pečená kuřecí prsa s citronem a bylinkami",
        "kcal":        230,
        "protein":     42,
        "carbs":       2,
        "fat":         6,
        "time":        "30 min",
        "servings":    2,
        "category":    "Hlavní jídla",
        "tags":        ["bez lepku", "proteinové", "nízkotučné", "příprava do zásoby"],
        "ingredients": [
            "2 kuřecí prsa (cca 200 g)",
            "1 citron",
            "3 stroužky česneku",
            "čerstvý tymián a rozmarýn",
            "2 lžíce olivového oleje",
            "sůl, pepř",
        ],
        "instructions": (
            "1. Troubu předehřej na 200 °C.\n"
            "2. Kuřecí prsa vylož do zapékací misky. Nařízni povrch mřížkově (neplný řez) – marináda lépe pronikne.\n"
            "3. Potři olivovým olejem smíseným s prolisovaným česnekem, solí a pepřem.\n"
            "4. Nakrájej citron na kolečka a rozlož kolem masa. Přidej větvičky tymiánu a rozmarýnu.\n"
            "5. Peč 22–25 minut. Přelij šťávou z dna v půlce pečení.\n"
            "6. Maso je hotové při vnitřní teplotě 74 °C. Nechej odpočinout 5 minut před krájením."
        ),
        "tip": "Odpočinutí masa před krájením zadrží šťávu uvnitř – maso zůstane šťavnaté.",
    },
    {
        "name":        "Vaječný salát na celozrnném toastu",
        "kcal":        290,
        "protein":     17,
        "carbs":       28,
        "fat":         12,
        "time":        "12 min",
        "servings":    2,
        "category":    "Snídaně",
        "tags":        ["proteinové", "rychlá příprava", "vegetariánské"],
        "ingredients": [
            "4 vejce",
            "2 lžíce řeckého jogurtu (nebo light majonézy)",
            "1 lžičce dijonské hořčice",
            "pažitka, sůl, pepř",
            "4 plátky celozrnného chleba",
            "salátové listy",
        ],
        "instructions": (
            "1. Vejce uvař natvrdo (10 minut), zchlaď pod studenou vodou a oloupal.\n"
            "2. Nakrájej na kostičky nebo rozmačkej vidličkou dle preference.\n"
            "3. Smíchej s jogurtem, hořčicí, nakrájenou pažitkou, solí a pepřem.\n"
            "4. Chléb opraž v toustovači.\n"
            "5. Na každý toast polož salátový list a pak štědrou vrstvu vaječného salátu.\n"
            "6. Posyp čerstvou pažitkou a podávej."
        ),
        "tip": "Řecký jogurt nahrazuje majonézu – méně tuku, více bílkovin.",
    },
    {
        "name":        "Zelené smoothie se špenátem a banánem",
        "kcal":        220,
        "protein":     6,
        "carbs":       46,
        "fat":         3,
        "time":        "5 min",
        "servings":    1,
        "category":    "Snídaně",
        "tags":        ["vegan", "bez lepku", "vitamíny", "rychlá příprava"],
        "ingredients": [
            "2 hrsti baby špenátu (cca 60 g)",
            "1 zralý banán",
            "150 ml mandlového nebo ovesného mléka",
            "½ jablka",
            "1 lžíce chia semínek",
            "šťáva z ½ citronu",
            "led (volitelně)",
        ],
        "instructions": (
            "1. Špenát propláchni a vhoď do mixéru jako první – lépe se rozmixuje.\n"
            "2. Přidej nakrájený banán, jablko, mléko, chia semínka a citronovou šťávu.\n"
            "3. Mixuj 45–60 sekund na highest rychlosti do úplně hladkého smoothie.\n"
            "4. Pokud je příliš husté, přidej lžíci mléka nebo vody.\n"
            "5. Nalij do sklenice a podávej ihned (nebo odnes v termosce)."
        ),
        "tip": "Citronová šťáva pomáhá vstřebávání železa ze špenátu.",
    },
    {
        "name":        "Vepřová panenka s pečenou zeleninou",
        "kcal":        370,
        "protein":     38,
        "carbs":       22,
        "fat":         13,
        "time":        "40 min",
        "servings":    2,
        "category":    "Hlavní jídla",
        "tags":        ["bez lepku", "proteinové", "česká klasika"],
        "ingredients": [
            "400 g vepřové panenky",
            "2 střední brambory",
            "1 červená cibule",
            "2 mrkve",
            "1 paprika",
            "olivový olej, rozmarýn, tymián",
            "sůl, pepř, česnek",
        ],
        "instructions": (
            "1. Troubu předehřej na 200 °C.\n"
            "2. Panenku osoliž, opepři a potři prolisovaným česnekem. Na pánvi ji ze všech stran krátce opeč (2 min/strana) do zlatohněda – takto zazní šťáva uvnitř.\n"
            "3. Zeleninu nakrájej na větší kousky, rozlož na plech s olejem, solí a bylinkami.\n"
            "4. Na zeleninu polož panenku a peč 20–25 minut.\n"
            "5. Maso nechej 5 minut odpočinout, pak nakrájej na medahyony (1,5 cm silné).\n"
            "6. Podávej s pečenou zeleninou a šťávou z pekáče."
        ),
        "tip": "Vepřová panenka je nejchudší kus vepřového masa na tuk.",
    },
    {
        "name":        "Quinoa bowl s pečenou cizrnou a tahini",
        "kcal":        420,
        "protein":     18,
        "carbs":       56,
        "fat":         14,
        "time":        "35 min",
        "servings":    2,
        "category":    "Hlavní jídla",
        "tags":        ["vegan", "bez lepku", "proteinové", "příprava do zásoby"],
        "ingredients": [
            "150 g quinoy",
            "400 g cizrny z konzervy",
            "1 paprika",
            "1 cuketa",
            "2 lžíce tahini",
            "citron, česnek",
            "kmín, paprika, olivový olej, sůl",
            "čerstvý koriandr nebo petržel",
        ],
        "instructions": (
            "1. Troubu předehřej na 200 °C.\n"
            "2. Cizrnu sceď, osuš a smíchej s olejem, kmínem, paprikou a solí. Rozlož na plech.\n"
            "3. Papriku a cuketu nakrájej na kostky, přidej na plech k cizrně.\n"
            "4. Peč 25 minut, v půlce promíchej – cizrna musí být křupavá.\n"
            "5. Quinou propláchni a uvař v dvojnásobku osolené vody (15 min).\n"
            "6. Tahini zálivka: smíchej tahini, citronovou šťávu, prolisovaný česnek a 2–3 lžíce vody do hladkého dresinku.\n"
            "7. Do misek dej quinou, přidej zeleninu a cizrnu, přelij tahini zálivkou a posyp bylinkami."
        ),
        "tip": "Pečená cizrna se hodí i jako křupavá svačina místo chipsů.",
    },
    {
        "name":        "Špenátová frittata se sýrem",
        "kcal":        250,
        "protein":     20,
        "carbs":       5,
        "fat":         17,
        "time":        "20 min",
        "servings":    2,
        "category":    "Snídaně",
        "tags":        ["proteinové", "bez lepku", "vegetariánské", "rychlá příprava"],
        "ingredients": [
            "5 vajec",
            "100 g baby špenátu",
            "50 g sýra (feta nebo eidam)",
            "½ cibule",
            "1 stroužek česneku",
            "1 lžíce olivového oleje",
            "sůl, pepř, muškátový oříšek",
        ],
        "instructions": (
            "1. Troubu předehřej na 180 °C.\n"
            "2. Vejce rozšlehej, přidej sůl, pepř a špetku muškátového oříšku.\n"
            "3. Na ohnivzdorné pánvi (nebo v malém pekáči) osmahni nadrobno nakrájenou cibuli na oleji 3 minuty, přidej česnek a špenát. Míchej dokud špenát nezvetší (1–2 min).\n"
            "4. Rozlož rovnoměrně po pánvi a přelij vejci.\n"
            "5. Navrch rozdrob nebo nastrouhej sýr.\n"
            "6. Peč v troubě 10–12 minut dokud není středu tuhá a okraje zlatavé.\n"
            "7. Nechej minutu vychladnout, nakrájej na klíny a podávej."
        ),
        "tip": "Frittata je studená stejně dobrá jako teplá – skvělá na pracovní oběd.",
    },
    {
        "name":        "Špenátová krémová polévka",
        "kcal":        160,
        "protein":     7,
        "carbs":       12,
        "fat":         9,
        "time":        "20 min",
        "servings":    3,
        "category":    "Polévky",
        "tags":        ["vegetariánské", "bez lepku", "vitamíny"],
        "ingredients": [
            "400 g čerstvého nebo mraženého špenátu",
            "1 cibule",
            "2 stroužky česneku",
            "600 ml zeleninového vývaru",
            "100 ml smetany ke šlehání (nebo rostlinné alternativy)",
            "1 lžíce olivového oleje",
            "muškátový oříšek, sůl, pepř",
        ],
        "instructions": (
            "1. Cibuli nakrájej nadrobno, česnek nasekej.\n"
            "2. V hrnci rozehřej olivový olej, osmahni cibuli 3 minuty do průhledna, přidej česnek a restuj 30 sekund.\n"
            "3. Přidej špenát (mražený bez rozmražení) a promíchej. Nech změknout 2–3 minuty.\n"
            "4. Zalijte vývar a přiveď k varu. Vař 5 minut.\n"
            "5. Odstaví a tyčovým mixérem rozmixuj do hladka.\n"
            "6. Vrátí na mírný plamen, vlij smetanu a zahřej – nevar.\n"
            "7. Dochucuj solí, pepřem a špetkou muškátového oříšku. Podávej s kapkou olivového oleje navrch."
        ),
        "tip": "Špenát je bohatý na železo, hořčík a kyselinu listovou.",
    },
    {
        "name":        "Mrkvová polévka se zázvorem a kokosem",
        "kcal":        190,
        "protein":     3,
        "carbs":       28,
        "fat":         8,
        "time":        "30 min",
        "servings":    4,
        "category":    "Polévky",
        "tags":        ["vegan", "bez lepku", "imunita"],
        "ingredients": [
            "600 g mrkve",
            "1 cibule",
            "3 cm čerstvého zázvoru",
            "200 ml kokosového mléka (light)",
            "600 ml zeleninového vývaru",
            "1 lžíce kokosového oleje",
            "limetka, kurkuma, sůl, pepř",
        ],
        "instructions": (
            "1. Mrkev oloupej a nakrájej na kolečka. Cibuli nakrájej nadrobno, zázvor nastrouhej.\n"
            "2. V hrnci rozehřej kokosový olej, osmahni cibuli 3 minuty.\n"
            "3. Přidej zázvor a kurkumu (1/2 lžičky), míchej 30 sekund.\n"
            "4. Přidej mrkev, zalijte vývar a přiveď k varu. Vař 20 minut do měkka.\n"
            "5. Rozmixuj tyčovým mixérem do hladka.\n"
            "6. Přilij kokosové mléko, prohřej a dochucuj solí a limetkovou šťávou.\n"
            "7. Podávej s kapkou kokosového mléka v misce a čerstvým koriandrem."
        ),
        "tip": "Mrkev a zázvor mají silné protizánětlivé a imunitní účinky.",
    },
    {
        "name":        "Pečené kuřecí stehno s batáty a rozmarýnem",
        "kcal":        440,
        "protein":     36,
        "carbs":       38,
        "fat":         14,
        "time":        "50 min",
        "servings":    2,
        "category":    "Hlavní jídla",
        "tags":        ["bez lepku", "proteinové", "příprava do zásoby"],
        "ingredients": [
            "4 kuřecí stehna (bez kůže)",
            "2 střední batáty",
            "1 červená cibule",
            "3 stroužky česneku",
            "2 větvičky čerstvého rozmarýnu",
            "2 lžíce olivového oleje",
            "sůl, pepř, paprika",
        ],
        "instructions": (
            "1. Troubu předehřej na 200 °C.\n"
            "2. Batáty oloupej a nakrájej na klínky, cibuli na čtvrtky.\n"
            "3. Vše (stehna i zeleninu) rozlož na velký plech, polijte olejem a okoření solí, pepřem a paprikou.\n"
            "4. Přidej celé stroužky česneku a větvičky rozmarýnu.\n"
            "5. Peč 40–45 minut, v půlce otočení stehna, aby se opekla z obou stran.\n"
            "6. Stehno je hotové, když ze zářezu vytéká čirá (ne růžová) šťáva.\n"
            "7. Nechej 5 minut odpočinout před podáváním."
        ),
        "tip": "Batáty dávají pomalou energii díky nízkému glykemickému indexu.",
    },
    {
        "name":        "Středomořský wrap s hummusem a zeleninou",
        "kcal":        340,
        "protein":     12,
        "carbs":       48,
        "fat":         11,
        "time":        "10 min",
        "servings":    1,
        "category":    "Svačiny",
        "tags":        ["vegetariánské", "rychlá příprava", "vláknina"],
        "ingredients": [
            "1 celozrnná tortilla (nebo lavash)",
            "3 lžíce hummuse",
            "50 g baby špenátu",
            "½ papriky",
            "¼ okurky",
            "50 g cherry rajčat",
            "10 oliv (kalamata)",
            "30 g fety",
            "citron, oregano",
        ],
        "instructions": (
            "1. Tortillu natolik ohřej v mikrovlnné troubě (20 sec) nebo na suché pánvi – bude poddajnější.\n"
            "2. Rovnoměrně rozetři hummus po celém povrchu, nechej okraje volné.\n"
            "3. Na spodní třetinu vrstvou pokryj špenát, pak nakrájenou papriku, okurku, rajčata a olivy.\n"
            "4. Rozdrob fetu navrch a posyp oreganem. Zakápni citronem.\n"
            "5. Zaroluj pevně – přelož boky dovnitř a pak sroluj od spodku nahoru.\n"
            "6. Překrojení diagonálně ukazuje náplň – podávej okamžitě nebo zabal do folie na cestu."
        ),
        "tip": "Hummus z cizrny dodává bílkoviny i vlákninu – skvělá kombinace pro výdrž.",
    },
    {
        "name":        "Energy balty s datlemi a ořechy",
        "kcal":        120,
        "protein":     3,
        "carbs":       16,
        "fat":         6,
        "time":        "15 min",
        "servings":    10,
        "category":    "Svačiny",
        "tags":        ["vegan", "bez pečení", "příprava předem", "přírodní sladidlo"],
        "ingredients": [
            "200 g medjool datlí (bez pecek)",
            "100 g mandlí (nebo kešu)",
            "50 g ovesných vloček",
            "2 lžíce kakaového prášku",
            "1 lžíce arašídového nebo mandlového másla",
            "špetka soli",
            "volitelně: kokos na obalení",
        ],
        "instructions": (
            "1. Pokud jsou datle tuhé, namočit je na 10 minut do teplé vody a osuš.\n"
            "2. Ořechy vlož do food processoru a pulzuj 10× na hrubé kousky – ne na prášek.\n"
            "3. Přidej datle, ovesné vločky, kakao, ořechové máslo a sůl.\n"
            "4. Zpracovávej do té doby, než vznikne lepivá kompaktní hmota (30–60 sekund). Pokud je příliš suchá, přidej lžíci vody.\n"
            "5. Mokrýma rukama formuj kuličky velikosti pingpongového míčku.\n"
            "6. Pro ozdobu obalí v strouhaném kokosu nebo kakaovém prášku.\n"
            "7. Dej do lednice na 30 minut ztuhnout. Uchovávej v uzavřené nádobě až 2 týdny."
        ),
        "tip": "Datle jsou přirozený zdroj rychlé energie bez přidaného cukru.",
    },
    {
        "name":        "Cottage cheese bowl s ovocem a granolou",
        "kcal":        270,
        "protein":     22,
        "carbs":       32,
        "fat":         5,
        "time":        "5 min",
        "servings":    1,
        "category":    "Snídaně",
        "tags":        ["proteinové", "rychlá příprava", "vápník"],
        "ingredients": [
            "200 g cottage cheese",
            "100 g sezonního ovoce (jahody, borůvky, broskev)",
            "25 g granoly (bez přidaného cukru)",
            "1 lžičce medu nebo javorového sirupu",
            "špetka skořice",
            "volitelně: lžíce chia semínek",
        ],
        "instructions": (
            "1. Cottage cheese přendej do misky.\n"
            "2. Ovoce nakrájej na sousto (jahody na čtvrtiny, broskev na kostičky).\n"
            "3. Rozlož ovoce po povrchu cottage cheese.\n"
            "4. Posyp granolou – přidej ji těsně před jídlem, aby zůstala křupavá.\n"
            "5. Zakápni medem, posyp skořicí a případně chia semínky.\n"
            "6. Konzumuj ihned."
        ),
        "tip": "Cottage cheese má méně tuku než tvaroh při zachování vysokého obsahu bílkovin.",
    },
]


def main():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 5432)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dbname=os.getenv("DB_NAME"),
        sslmode="require",
    )
    cur = conn.cursor()

    # 1. Vytvoř tabulku
    cur.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id           SERIAL PRIMARY KEY,
            name         TEXT    NOT NULL,
            kcal         INTEGER NOT NULL DEFAULT 0,
            protein      INTEGER NOT NULL DEFAULT 0,
            carbs        INTEGER NOT NULL DEFAULT 0,
            fat          INTEGER NOT NULL DEFAULT 0,
            time         TEXT,
            servings     INTEGER,
            category     TEXT,
            tags         JSONB   DEFAULT '[]',
            ingredients  JSONB   DEFAULT '[]',
            instructions TEXT,
            tip          TEXT
        )
    """)
    conn.commit()
    print("✓ Tabulka recipes zkontrolována / vytvořena.")

    # 2. Zkontroluj zda je prázdná
    cur.execute("SELECT COUNT(*) FROM recipes")
    count = cur.fetchone()[0]
    if count > 0:
        print(f"  Tabulka již obsahuje {count} receptů. Přidám pouze nové.")

    # 3. Načti stávající recepty z nutrition_utils
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from utils.nutrition_utils import _HEALTHY_RECIPES

    # 4. Vyber jen ty, co ještě nejsou v DB
    cur.execute("SELECT name FROM recipes")
    existing_names = {row[0] for row in cur.fetchall()}

    all_recipes = list(_HEALTHY_RECIPES) + NEW_RECIPES
    to_insert = [r for r in all_recipes if r["name"] not in existing_names]

    if not to_insert:
        print("  Všechny recepty jsou již v databázi. Nic k přidání.")
        cur.close()
        conn.close()
        return

    # 5. Vlož
    for r in to_insert:
        cur.execute(
            """
            INSERT INTO recipes
                (name, kcal, protein, carbs, fat, time, servings,
                 category, tags, ingredients, instructions, tip)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                r["name"],
                int(r["kcal"]),
                int(r["protein"]),
                int(r["carbs"]),
                int(r["fat"]),
                r.get("time"),
                r.get("servings"),
                r.get("category"),
                json.dumps(r.get("tags", []), ensure_ascii=False),
                json.dumps(r.get("ingredients", []), ensure_ascii=False),
                r.get("instructions"),
                r.get("tip"),
            )
        )
        print(f"  + {r['name']}")

    conn.commit()
    print(f"\n✓ Přidáno {len(to_insert)} receptů do databáze.")
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
