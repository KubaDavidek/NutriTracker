"""
nutrition_utils.py – Výpočet mikroživin a katalog zdravých českých receptů.
"""

import random
from typing import Dict, List


# ══════════════════════════════════════════════════════════════════════════════
# MIKROŽIVINY – orientační odhad z makronutrientů
# ══════════════════════════════════════════════════════════════════════════════

def estimate_micronutrients(totals: Dict) -> Dict:
    """
    Orientační odhad mikroživin a minerálů z denních makronutrientů.
    DDD = doporučená denní dávka pro průměrného dospělého.
    """
    kcal    = totals.get("kcal",    0)
    carbs   = totals.get("carbs",   0)
    fat     = totals.get("fat",     0)
    protein = totals.get("protein", 0)

    return {
        # ── Cukry ──────────────────────────────────────────────────────────
        "sugars":        round(carbs * 0.35, 1),
        "sugars_dv":     50,
        "sugars_unit":   "g",

        # ── Vláknina ───────────────────────────────────────────────────────
        "fiber":         round(kcal * 0.025, 1),
        "fiber_dv":      30,
        "fiber_unit":    "g",

        # ── Nenasycené tuky ────────────────────────────────────────────────
        "unsat_fat":     round(fat * 0.65, 1),
        "unsat_fat_dv":  45,
        "unsat_fat_unit":"g",

        # ── Nasycené tuky ──────────────────────────────────────────────────
        "sat_fat":       round(fat * 0.35, 1),
        "sat_fat_dv":    20,
        "sat_fat_unit":  "g",

        # ── Vitamín C ──────────────────────────────────────────────────────
        "vitamin_c":     round(carbs * 0.18, 1),
        "vitamin_c_dv":  80,
        "vitamin_c_unit":"mg",

        # ── Vitamín B12 (odhad z bílkovin – živočišné zdroje) ─────────────
        "vitamin_b12":   round(protein * 0.006, 2),
        "vitamin_b12_dv":2.4,
        "vitamin_b12_unit":"µg",

        # ── Sodík ──────────────────────────────────────────────────────────
        "sodium":        round(kcal * 0.45),
        "sodium_dv":     2000,
        "sodium_unit":   "mg",

        # ── Vápník ─────────────────────────────────────────────────────────
        "calcium":       round(kcal * 0.10),
        "calcium_dv":    1000,
        "calcium_unit":  "mg",

        # ── Železo ─────────────────────────────────────────────────────────
        "iron":          round(kcal * 0.006, 1),
        "iron_dv":       14,
        "iron_unit":     "mg",

        # ── Draslík ────────────────────────────────────────────────────────
        "potassium":     round(kcal * 0.35),
        "potassium_dv":  3500,
        "potassium_unit":"mg",

        # ── Hořčík ─────────────────────────────────────────────────────────
        "magnesium":     round(kcal * 0.048),
        "magnesium_dv":  375,
        "magnesium_unit":"mg",

        # ── Fosfor ─────────────────────────────────────────────────────────
        "phosphorus":    round(kcal * 0.10),
        "phosphorus_dv": 700,
        "phosphorus_unit":"mg",
    }


# ══════════════════════════════════════════════════════════════════════════════
# ZDRAVÉ ČESKÉ RECEPTY – statický katalog
# ══════════════════════════════════════════════════════════════════════════════

_HEALTHY_RECIPES: List[Dict] = [
    {
        "name":        "Zeleninová polévka s quinoou",
        "kcal":        210,
        "protein":     8,
        "carbs":       34,
        "fat":         4,
        "time":        "25 min",
        "servings":    2,
        "category":    "Polévky",
        "tags":        ["vegan", "bez lepku", "nízkotučné"],
        "ingredients": [
            "200 g quinoa",
            "2 mrkve",
            "1 cuketa",
            "1 cibule",
            "2 stroužky česneku",
            "1 l zeleninového vývaru",
            "sůl, pepř, tymián",
        ],
        "instructions": (
            "1. Quinou propláchni pod studenou vodou v sítku, dokud voda nezůstane čistá – zbavíš ji hořkosti.\n"
            "2. Cibuli oloupej a nakrájej nadrobno, česnek prolisuj nebo nasekej.\n"
            "3. V hrnci rozehřej lžičku olivového oleje na středním plameni. Osmahni cibuli 3 minuty do průhledna, poté přidej česnek a míchej dalších 30 sekund.\n"
            "4. Mrkev oloupej a nakrájej na kolečka (cca 3–4 mm), cuketu nakrájej na půlměsíce podobné velikosti.\n"
            "5. Přidej mrkev do hrnce a restuj 2 minuty. Pak přidej cuketu a promíchej.\n"
            "6. Zalijte zeleninový vývar, přidej quinou a přiveď k varu.\n"
            "7. Stáhni plamen, přikryj poklicí a vař 15 minut, dokud quinoa nenapuchne a zelenina nezměkne.\n"
            "8. Dochucuj solí, pepřem a sušeným tymiánem. Podávej horké, posypané čerstvou petrželkou."
        ),
        "tip": "Quinoa dodá plnohodnotné bílkoviny – skvělé pro regeneraci.",
    },
    {
        "name":        "Pečený losos s brokolicí a citrónem",
        "kcal":        320,
        "protein":     32,
        "carbs":       6,
        "fat":         18,
        "time":        "30 min",
        "servings":    2,
        "category":    "Hlavní jídla",
        "tags":        ["proteinové", "bez lepku", "omega-3"],
        "ingredients": [
            "2× filet lososa (cca 150 g)",
            "300 g brokolice",
            "1 citron",
            "1 lžíce olivového oleje",
            "česnek, sůl, paprika",
        ],
        "instructions": (
            "1. Troubu předehřej na 200 °C (horkovzduch 185 °C). Plech vystlej pečicím papírem.\n"
            "2. Filety lososa osušte papírovou utěrkou – lépe se pak zatáhnou a nerozkypí se.\n"
            "3. V misce smíchej olivový olej, prolisovaný česnek, sladkou papriku, sůl a pepř. Touto marinádou potři lososa ze všech stran.\n"
            "4. Brokolici rozeběr na menší růžičky, příliš tučné stonky oloupen a nakrájej na kolečka.\n"
            "5. Brokolici vyhodit postříkat trochou oleje, osolit a promíchat.\n"
            "6. Na plech rozlož brokolici do jedné vrstvy, na ni polož filetiky lososa kůží dolů.\n"
            "7. Peč 18–22 minut – losos je hotový, až se maso lehce odlupuje vidličkou a doprostřed je neprůhledné.\n"
            "8. Vytáhni z trouby, bohatě pokropte čerstvou citrónovou šťávou a podávej ihned."
        ),
        "tip": "Losos je bohatý na omega-3 mastné kyseliny a vitamín D.",
    },
    {
        "name":        "Ovesná kaše s borůvkami a ořechy",
        "kcal":        290,
        "protein":     9,
        "carbs":       48,
        "fat":         7,
        "time":        "10 min",
        "servings":    1,
        "category":    "Snídaně",
        "tags":        ["vegan", "vysokovláknité", "antioxidanty"],
        "ingredients": [
            "80 g ovesných vloček",
            "250 ml rostlinného mléka",
            "100 g borůvek",
            "20 g vlašských ořechů",
            "1 lžička medu",
            "špetka skořice",
        ],
        "instructions": (
            "1. Vloček odměř do malého hrnce, přilij rostlinné mléko a na středním plameni přiveď k varu za stálého míchání.\n"
            "2. Ihned po prvním bublání stáhni plamen na minimum a nech vloček vařit 5–7 minut. Občas promíchej, aby se nelepily ke dnu.\n"
            "3. Jakmile kaše dosáhne krémové konzistence (lze přidat trochu mléka, pokud je příliš hustá), odstaví z plamene.\n"
            "4. Přendej do misky a nechej minutu odstát – kaše se trochu zhoustne.\n"
            "5. Posyp borůvkami (čerstvé i mražené fungují; mražené přidej rovnou do hrnce 2 minuty před koncem vaření).\n"
            "6. Vlašské ořechy hrubě nalámej rukou a rozhoď po povrchu.\n"
            "7. Zakápni medem, posyp špetkou skořice a podávej hned."
        ),
        "tip": "Ovesné vločky zpomalují vstřebávání cukru – skvělý start dne.",
    },
    {
        "name":        "Čočkový salát s rajčaty a špenátem",
        "kcal":        260,
        "protein":     16,
        "carbs":       40,
        "fat":         5,
        "time":        "20 min",
        "servings":    2,
        "category":    "Saláty",
        "tags":        ["vegan", "proteinové", "hodně vlákniny"],
        "ingredients": [
            "200 g vařené zelené čočky",
            "2 rajčata",
            "100 g baby špenátu",
            "½ cibule",
            "2 lžíce olivového oleje",
            "1 lžíce citrónové šťávy",
            "sůl, pepř, kmín",
        ],
        "instructions": (
            "1. Pokud vaříš čočku od základu: propláchni ji, zalijte studenou vodou (dvojnásobek objemu), přiveď k varu a vař 15–18 minut do měkka. Sceď a nech vychladnout.\n"
            "2. Cibuli oloupej a nakrájej co nejnadrobněji. Pokud nechceš příliš ostrou chuť, namočit ji na 5 minut do studené vody a odceď.\n"
            "3. Rajčata nakrájej na kostičky (cca 1 cm), šťávu z nich sebereme do mísy – je součástí zálivky.\n"
            "4. V malé misce smíchej olivový olej, citrónovou šťávu, špetku kmínu, sůl a pepř. Zálivku ochutnej a uprav kyselost.\n"
            "5. Do velké mísy dej špenát, přidej vychladlou čočku, rajčata a cibuli.\n"
            "6. Přelij zálivkou a opatrně promíchej – špenát nesmí zvetšet.\n"
            "7. Nechej salát 5 minut odležet, aby se chutě propojily, pak podávej."
        ),
        "tip": "Čočka obsahuje více bílkovin než většina luštěnin.",
    },
    {
        "name":        "Kuřecí vývar se zeleninou a nudlemi",
        "kcal":        180,
        "protein":     12,
        "carbs":       8,
        "fat":         3,
        "time":        "40 min",
        "servings":    4,
        "category":    "Polévky",
        "tags":        ["bez tuku", "lehce stravitelné", "bohaté na minerály"],
        "ingredients": [
            "400 g kuřecích prsíček",
            "2 mrkve",
            "1 petržel",
            "¼ celeru",
            "1 cibule",
            "100 g celozrnných nudlí",
            "sůl, pepř, bobkový list",
        ],
        "instructions": (
            "1. Kuřecí prsa propláchni pod studenou vodou a vložte do velkého hrnce. Zalijte 1,5 l studené vody.\n"
            "2. Cibuli rozkrojit napůl (nemusíš loupat – slupka dá vývaru barvu). Mrkev, petržel a celer oloupej, nechej vcelku nebo hrubě nakrájej.\n"
            "3. Do hrnce přidej veškerou zeleninu, bobkový list, celý pepř a lžičku soli. Přiveď pomalu k varu.\n"
            "4. Jakmile se tvoří šedá pěna, sbírej ji lžící – vývar bude čistý a nehořký.\n"
            "5. Stáhni plamen na minimum, přikryj pokličkou na škvírku a vař 25–30 minut.\n"
            "6. Maso vyndej, nechej chvíli vychladnout a rozkrájej na kousky nebo roztrhej vidličkou. Zeleninu vyndej a nakrájej na kolečka.\n"
            "7. Vývar přeceď přes sítko, vrátí zpět do hrnce. Přidej maso, zeleninu a nudle.\n"
            "8. Vař dalších 7–8 minut, dokud nudle nezměknou. Dochucuj solí a pepřem a podávej horké."
        ),
        "tip": "Vývar pomáhá s hydratací a dodává důležité elektrolyty.",
    },
    {
        "name":        "Tvarohová pomazánka s pažitkou na celozrnném chlebu",
        "kcal":        220,
        "protein":     18,
        "carbs":       22,
        "fat":         4,
        "time":        "5 min",
        "servings":    1,
        "category":    "Snídaně",
        "tags":        ["proteinové", "probiotika", "rychlá příprava"],
        "ingredients": [
            "150 g nízkotučného tvarohu",
            "2 lžíce pažitky",
            "1 stroužek česneku",
            "sůl, pepř",
            "2 plátky celozrnného chleba",
        ],
        "instructions": (
            "1. Tvaroh přendej do misky a vidličkou nebo metličkou ho rozmíchej do hladka – tak se lépe natírá.\n"
            "2. Česnek oloupej a prolisuj přímo do tvarohu (nebo nastrouhej na jemném struhadle pro mírnější chuť).\n"
            "3. Pažitku zasekej nadrobno a přidej k tvarohu spolu se solí a pepřem.\n"
            "4. Vše dobře promíchej a ochutnaj – podle chuti přidej ještě sůl nebo citronovou šťávu pro svěžest.\n"
            "5. Plátky celozrnného chleba lehce opraž v toustovači nebo na suché pánvi.\n"
            "6. Pomazánku štědře rozetři na chléb a podávej okamžitě."
        ),
        "tip": "Tvaroh je vynikající zdroj kaseinu – zasytí na dlouho.",
    },
    {
        "name":        "Zapečená cuketa s rajčaty a mozzarellou",
        "kcal":        240,
        "protein":     14,
        "carbs":       10,
        "fat":         12,
        "time":        "35 min",
        "servings":    2,
        "category":    "Hlavní jídla",
        "tags":        ["vegetariánské", "nízkosacharidové", "vápník"],
        "ingredients": [
            "2 střední cukety",
            "3 rajčata",
            "125 g light mozzarelly",
            "2 lžíce olivového oleje",
            "bazalka, sůl, pepř",
            "1 stroužek česneku",
        ],
        "instructions": (
            "1. Troubu předehřej na 190 °C. Zapékací mísu lehce vymaž olejem.\n"
            "2. Cukety nakrájej na plátky silné 5–6 mm, rozlož na papír a z obou stran osolí. Nech 10 minut odstát – pustí přebytečnou vodu. Pak osušit papírovou utěrkou.\n"
            "3. Rajčata nakrájej na plátky stejné tloušťky. Mozzarellu rovněž nakrájej na plátky.\n"
            "4. Do zapékací mísy skládej střídavě plátky cukety, rajčete a mozzarelly jako šindele – mírně překryté.\n"
            "5. Česnek prolisuj do olivového oleje, přidej pepř a tímto olejem přelij celé zapékání.\n"
            "6. Posyp čerstvou nebo sušenou bazalkou a případně trochou soli.\n"
            "7. Peč 22–25 minut, dokud cuketa nezměkne a sýr nezačne bublat a zlatnout na okrajích.\n"
            "8. Před podáváním nechej 5 minut vychladnout, aby se chutě ustálily."
        ),
        "tip": "Cuketa má minimum kalorií a spoustu draslíku.",
    },
    {
        "name":        "Tofu stir-fry s paprikami a hnědou rýží",
        "kcal":        350,
        "protein":     16,
        "carbs":       42,
        "fat":         10,
        "time":        "25 min",
        "servings":    2,
        "category":    "Hlavní jídla",
        "tags":        ["vegan", "proteinové", "bez lepku"],
        "ingredients": [
            "250 g pevného tofu",
            "2 barevné papriky",
            "1 cibule",
            "2 stroužky česneku",
            "200 g hnědé rýže (uvařené)",
            "2 lžíce sójové omáčky (bez lepku)",
            "1 lžička sezamového oleje",
            "zázvor, chilli",
        ],
        "instructions": (
            "1. Tofu vyndej z obalu, obal do kuchyňských ubrousků a polož na něj těžký hrnec na 10 minut – vymačká se přebytečná voda a tofu se lépe osmahne.\n"
            "2. Osušené tofu nakrájej na kostky 2×2 cm. Papriky nakrájej na proužky, cibuli na půlkolečka, česnek nasekej, zázvor nastrouhej.\n"
            "3. Rozehřej pánev (ideálně wok) na vysokém plameni – musí být opravdu horká. Přidej lžičku rostlinného oleje.\n"
            "4. Tofu opékej bez míchání 3–4 minuty, dokud se nezatáhne a nezlátne. Pak otoč a opékej ještě 2 minuty z druhé strany. Vyndej na talíř.\n"
            "5. Do té samé pánve přidej trochu oleje, osmahni cibuli 2 minuty. Přidej česnek a zázvor, míchej 30 sekund.\n"
            "6. Přidej papriky a restuj na vysokém plameni 3–4 minuty – zelenina má zůstat křupavá.\n"
            "7. Vrátil tofu zpět, přilij sójovou omáčku a chilli podle chuti. Promíchej a nech 1 minutu propéct dohromady.\n"
            "8. Odstaví z ohně, zakápni sezamovým olejem. Podávej na uvařené hnědé rýži."
        ),
        "tip": "Tofu je kompletní rostlinný zdroj bílkovin s nízkým obsahem tuku.",
    },
    {
        "name":        "Řecký jogurt s granolou a medem",
        "kcal":        280,
        "protein":     14,
        "carbs":       35,
        "fat":         6,
        "time":        "3 min",
        "servings":    1,
        "category":    "Svačiny",
        "tags":        ["probiotika", "vápník", "rychlá příprava"],
        "ingredients": [
            "200 g řeckého jogurtu (2 %)",
            "30 g domácí granoly (bez přidaného cukru)",
            "100 g sezonního ovoce",
            "1 lžička medu",
            "špetka skořice",
        ],
        "instructions": (
            "1. Řecký jogurt přendej do hluboké misky nebo sklenice (parfétový pohár vypadá skvěle).\n"
            "2. Ovoce připrav dle sezóny: jahody nakrájej na čtvrtiny, borůvky nechej celé, mango nebo broskev na kostičky.\n"
            "3. Na jogurt syp granolu – přidej ji těsně před podáváním, aby zůstala křupavá.\n"
            "4. Rozlož ovoce po povrchu granoly.\n"
            "5. Zakápni lžičkou medu a posyp špetkou skořice.\n"
            "6. Podávej okamžitě nebo přechovávej v lednici bez granoly (přidej ji až před jídlem)."
        ),
        "tip": "Řecký jogurt má dvojnásob bílkovin oproti normálnímu jogurtu.",
    },
    {
        "name":        "Pohankové rizoto se špenátem a houbami",
        "kcal":        310,
        "protein":     12,
        "carbs":       52,
        "fat":         6,
        "time":        "30 min",
        "servings":    2,
        "category":    "Hlavní jídla",
        "tags":        ["bezlepkové", "vegan", "vitamíny skupiny B"],
        "ingredients": [
            "200 g pohanky",
            "200 g špenátu",
            "150 g žampiónů",
            "1 cibule",
            "400 ml zeleninového vývaru",
            "1 lžíce olivového oleje",
            "sůl, pepř, muškátový oříšek",
        ],
        "instructions": (
            "1. Pohanku propláchni pod studenou vodou v sítku, dokud voda neteče čistá.\n"
            "2. Cibuli nakrájej nadrobno, žampióny na plátky (4–5 mm).\n"
            "3. V hlubší pánvi nebo hrnci rozehřej olivový olej na středním plameni. Osmahni cibuli 3 minuty do zlatova.\n"
            "4. Přidej žampióny a suš je na vysokém plameni 4–5 minut bez míchání – ztratí vodu a začnou se opékat. Pak promíchej a osmahni ze všech stran.\n"
            "5. Přidej proplachnutou pohanku a promíchej, aby se obalila olejem (1 minuta).\n"
            "6. Zalijte zeleninový vývar, přiveď k varu a stáhni plamen na minimum.\n"
            "7. Vař přikryté 12–15 minut, dokud pohanka nevstřebá vývar a nezměkne. Pokud bude příliš suchá, přidej trochu vody.\n"
            "8. Vlož čerstvý nebo rozmražený špenát, promíchej a nech 2 minuty zvetšet pod pokličkou.\n"
            "9. Dochucuj solí, pepřem a špetkou muškátového oříšku. Podávej horké."
        ),
        "tip": "Pohanka je bezlepková a obsahuje všechny esenciální aminokyseliny.",
    },

    # ── Nové recepty ────────────────────────────────────────────────────────────

    {
        "name":        "Vaječná omeleta se špenátem a fetou",
        "kcal":        280,
        "protein":     22,
        "carbs":       4,
        "fat":         19,
        "time":        "10 min",
        "servings":    1,
        "category":    "Snídaně",
        "tags":        ["proteinové", "bez lepku", "rychlá příprava"],
        "ingredients": [
            "3 vejce",
            "50 g baby špenátu",
            "40 g fety",
            "1 lžička olivového oleje",
            "sůl, pepř, chilli vločky",
        ],
        "instructions": (
            "1. Vejce rozklepni do misky, přidej špetku soli a pepře, metličkou prošlehej do homogenní hmoty.\n"
            "2. Špenát propláchni a osuš. Fetu rozdrob vidličkou na drobné kousky.\n"
            "3. Nepřilnavou pánev (průměr 20–22 cm) rozehřej na středním plameni, přidej olivový olej.\n"
            "4. Jakmile olej lehce zavlní, vlij vejce. Okraje začnou okamžitě tuhnout – stáhni je špachtlí ke středu a nakloň pánev, aby tekuté vejce zaplnilo okraje.\n"
            "5. Jakmile je povrch ještě lehce lesklý (ne úplně tuhý), pokryj polovinu špenátem a drobky fety.\n"
            "6. Přelož omeletu na půl, přitlač lehce a nech ještě 30 sekund dojít.\n"
            "7. Přendej na talíř, posyp chilli vločkami a podávej ihned."
        ),
        "tip": "Vejce jsou kompletní zdroj všech esenciálních aminokyselin.",
    },
    {
        "name":        "Smoothie bowl s borůvkami a proteinem",
        "kcal":        340,
        "protein":     24,
        "carbs":       48,
        "fat":         5,
        "time":        "7 min",
        "servings":    1,
        "category":    "Snídaně",
        "tags":        ["antioxidanty", "proteinové", "bez lepku"],
        "ingredients": [
            "150 g mražených borůvek",
            "1 mražený banán",
            "150 g řeckého jogurtu",
            "1 odměrka (30 g) vanilkového whey proteinu",
            "50 ml mandlového mléka",
            "toping: granola, čerstvé borůvky, plátky mandlí",
        ],
        "instructions": (
            "1. Všechny ingredience do mixéru v pořadí: nejprve jogurt a mléko, pak mražené ovoce a úplně nakonec protein.\n"
            "2. Mixuj na nejvyšší rychlost 45–60 sekund, dokud nevznikne hladká, hustá hmota. Pokud je příliš hustá, přidej lžíci mléka.\n"
            "3. Konzistence musí být výrazně hustší než smoothie – má stát lžíce vzpřímeně.\n"
            "4. Přendej do misky (studené misky pomáhají udržet chlad déle).\n"
            "5. Ozdobení: malou hrstku granoly nasypej na jednu stranu, čerstvé borůvky na druhou, plátky mandlí rozhoď po povrchu.\n"
            "6. Podávej okamžitě – smoothie bowl rychle roztává."
        ),
        "tip": "Mražené ovoce uchovává všechny antioxidanty stejně jako čerstvé.",
    },
    {
        "name":        "Avokádový toast s vejcem",
        "kcal":        390,
        "protein":     18,
        "carbs":       32,
        "fat":         22,
        "time":        "12 min",
        "servings":    1,
        "category":    "Snídaně",
        "tags":        ["zdravé tuky", "vláknina", "rychlá příprava"],
        "ingredients": [
            "2 plátky celozrnného chleba",
            "1 zralé avokádo",
            "2 vajíčka",
            "½ limetky nebo citronu",
            "chilli vločky, sůl, pepř",
            "volitelně: cherry rajčata, ředkvičky",
        ],
        "instructions": (
            "1. Chleba opraž v toustovači nebo na suché pánvi do zlatohněda.\n"
            "2. Avokádo překroj napůl, vyjmi pecku, vydlabej dužinu lžící do misky. Přidej lžíci citrusové šťávy, špetku soli a hrubě rozmačkej vidličkou – nech strukturu, není třeba úplně hladká pasta.\n"
            "3. Vejce uvaž na hniličku (3 min v 90°C vodě s lžící octa) nebo připrav volské oko na lžičce oleje.\n"
            "4. Avokádovou směs rozetři bohatě na oba plátky toastu.\n"
            "5. Na každý toast polož jedno vejce, posyp chilli vločkami a čerstvě mletým pepřem.\n"
            "6. Volitelně ozdobení cherry rajčaty nebo tenkými plátky ředkviček."
        ),
        "tip": "Avokádo obsahuje mononenasycené kyseliny snižující LDL cholesterol.",
    },
    {
        "name":        "Overnight oats s chia a malinami",
        "kcal":        350,
        "protein":     15,
        "carbs":       55,
        "fat":         8,
        "time":        "5 min + přes noc",
        "servings":    1,
        "category":    "Snídaně",
        "tags":        ["vegan", "vysokovláknité", "příprava předem"],
        "ingredients": [
            "70 g celých ovesných vloček",
            "200 ml rostlinného mléka",
            "1 lžíce chia semínek",
            "1 lžíce javorového sirupu",
            "100 g čerstvých nebo mražených malin",
        ],
        "instructions": (
            "1. Do sklenice nebo uzavíratelné nádoby nasypej ovesné vločky.\n"
            "2. Přidej chia semínka a promíchej.\n"
            "3. Zalij rostlinným mlékem, přidej javorový sirup a důkladně promíchej. Vočky musí být celé ponořené.\n"
            "4. Uzavři a dej do lednice na minimálně 6 hodin, ideálně přes noc.\n"
            "5. Ráno promíchej – kaše ztvrdne, přidej lžíci mléka pokud chceš řidší konzistenci.\n"
            "6. Navrch dej maliny (mražené nechej 5 minut rozmrznout). Podávej za studena."
        ),
        "tip": "Chia semínka nabobtnají a vytvoří gelovou strukturu bohatou na omega-3.",
    },
    {
        "name":        "Kuřecí burrito bowl",
        "kcal":        480,
        "protein":     38,
        "carbs":       52,
        "fat":         10,
        "time":        "25 min",
        "servings":    2,
        "category":    "Hlavní jídla",
        "tags":        ["proteinové", "bez lepku", "příprava do zásoby"],
        "ingredients": [
            "300 g kuřecích prsou",
            "200 g vařené hnědé rýže",
            "200 g černých fazolí (konzerva)",
            "1 červená paprika",
            "1 avokádo",
            "100 g kukuřice (konzerva)",
            "limetka, koriandr, chilli, kmín, česnek",
        ],
        "instructions": (
            "1. Kuřecí prsa nakrájej na tenké proužky. V misce smíchej kmín, chilli, prolisovaný česnek, sůl a pepř. Kuře obal v koření.\n"
            "2. Na pánvi s trochou oleje osmahni kuře na vysokém plameni 3–4 minuty z každé strany. Maso musí být uvnitř bílé, ne růžové. Odlož na talíř.\n"
            "3. Papriků nakrájej na proužky a osmahni ve stejné pánvi 3 minuty – má zůstat lehce křupavá.\n"
            "4. Fazole sceď a proplácni, kukuřici sceď.\n"
            "5. Avokádo rozmačkej s limetkovou šťávou a solí na guacamole.\n"
            "6. Do misek (bowls) naskládej rýži jako základ. Přidej řadami: kuře, fazole, kukuřici, papriku.\n"
            "7. Na střed dej guacamole, přikap limetkovou šťávou a posyp čerstvým koriandrem."
        ),
        "tip": "Černé fazole dodávají vlákninu a zpomalují vstřebávání sacharidů.",
    },
    {
        "name":        "Pečená treska s dušenou zeleninou",
        "kcal":        220,
        "protein":     32,
        "carbs":       12,
        "fat":         4,
        "time":        "25 min",
        "servings":    2,
        "category":    "Hlavní jídla",
        "tags":        ["bez lepku", "nízkotučné", "proteinové"],
        "ingredients": [
            "2× filet tresky (cca 160 g)",
            "1 cuketa",
            "1 červená paprika",
            "150 g cherry rajčat",
            "citron, olivový olej",
            "tymián, sůl, pepř",
        ],
        "instructions": (
            "1. Troubu předehřej na 200 °C. Plech vystlej papírem na pečení.\n"
            "2. Cuketu a papriku nakrájej na kostky (2 cm), cherry rajčata nechej celá.\n"
            "3. Zeleninu rozlož na plech, pokrop lžičkou oleje, osolí a opepi.\n"
            "4. Dej péct na 10 minut.\n"
            "5. Filety tresky osuš, potři trochou oleje, posyp tymiánem, solí a zakápni citronem.\n"
            "6. Přidej tresku na plech k zelenině a peč dalších 12–15 minut, dokud se ryba lehce nerozlamuje vidličkou.\n"
            "7. Podávej v pekáči – šťáva z rajčat vytvoří přirozenou omáčku."
        ),
        "tip": "Treska je jednou z nejchudších ryb na tuk – ideální pro redukční diety.",
    },
    {
        "name":        "Hovězí stir-fry s brokolicí a zázvorem",
        "kcal":        420,
        "protein":     34,
        "carbs":       22,
        "fat":         18,
        "time":        "20 min",
        "servings":    2,
        "category":    "Hlavní jídla",
        "tags":        ["bez lepku", "proteinové", "rychlá příprava"],
        "ingredients": [
            "300 g libového hovězího (zadní nebo svíčková)",
            "300 g brokolice",
            "2 stroužky česneku",
            "2 cm čerstvého zázvoru",
            "2 lžíce sójové omáčky (bez lepku)",
            "1 lžičce sezamového oleje",
            "1 lžíce rýžového octa",
            "sesam na posypání",
        ],
        "instructions": (
            "1. Hovězí nakrájej přes vlákno na tenké proužky (1–2 mm). Lehce ozkoněj lžící škrobu pro lepší texturu.\n"
            "2. Smíchej sójovou omáčku, rýžový ocet a lžičku medu – to bude omáčka. Odlož.\n"
            "3. Brokolici rozeber na malé růžičky. Blanšíruj 2 minuty v osolené vařící vodě, sceď a osuš.\n"
            "4. Wok nebo velká pánev musí být opravdu horká (kouří se z ní). Přidej lžíci oleje.\n"
            "5. Hovězí osmahni 1–2 minuty za stálého míchání – chceš zatáhlé kusy, ne šedé a vylouhované. Vyndej.\n"
            "6. Ve stejném woku osmahni česnek a nastrouhaný zázvor 30 sekund, přidej brokolici a míchej 2 minuty.\n"
            "7. Vrátil hovězí zpět, přilij omáčku, všechno promíchej a nech 1 minutu propéct.\n"
            "8. Odstaví, pokap sezamovým olejem a posyp sesamem. Podávej s hnědou rýží."
        ),
        "tip": "Zázvor má protizánětlivé účinky a podporuje trávení.",
    },
    {
        "name":        "Plněné papriky s krůtím masem a quinoou",
        "kcal":        320,
        "protein":     28,
        "carbs":       30,
        "fat":         8,
        "time":        "45 min",
        "servings":    2,
        "category":    "Hlavní jídla",
        "tags":        ["bez lepku", "proteinové", "příprava do zásoby"],
        "ingredients": [
            "2 velké červené papriky",
            "200 g mletého krůtího masa",
            "100 g uvařené quinoi",
            "1 cibule",
            "2 rajčata",
            "50 g parmazánu",
            "oregano, bazalka, sůl, pepř",
        ],
        "instructions": (
            "1. Troubu předehřej na 190 °C.\n"
            "2. Paprikám usekni vrch (zachovej víčko), vydlabej semínka a bílé blány.\n"
            "3. Cibuli nakrájej nadrobno, rajčata na kostičky.\n"
            "4. Na pánvi osmahni cibuli do zlatova, přidej mleté maso a restuj za míchání 5–7 minut, dokud není celé propečené.\n"
            "5. Přidej rajčata, quinou, oregano, bazalku, sůl a pepř. Prohřej a propoj 2 minuty.\n"
            "6. Naplň papriky masovou směsí, přikryj víčky.\n"
            "7. Postav do zapékací misky, přilij trochu vody na dno a peč 25–28 minut.\n"
            "8. Posledních 5 minut odkryj víčka, posypej parmazánem a nechej zapéct do zlatova."
        ),
        "tip": "Quinoa obsahuje všechny esenciální aminokyseliny, takže náplň je výživnostně kompletní.",
    },
    {
        "name":        "Tuňákový salát s avokádem a vejcem",
        "kcal":        310,
        "protein":     35,
        "carbs":       6,
        "fat":         16,
        "time":        "15 min",
        "servings":    2,
        "category":    "Saláty",
        "tags":        ["bez lepku", "proteinové", "nízkosacharidové"],
        "ingredients": [
            "2× 80 g tuňáka v nálevu (konzerva)",
            "1 avokádo",
            "3 natvrdo uvařená vejce",
            "100 g cherry rajčat",
            "½ okurky",
            "1 lžíce olivového oleje",
            "citron, sůl, pepř, dijonská hořčice",
        ],
        "instructions": (
            "1. Vejce uvař natvrdo (9–10 minut), oloupal a nakrájej na čtvrtiny.\n"
            "2. Tuňák sceď a rozmačkej vidličkou.\n"
            "3. Avokádo nakrájej na kostky nebo plátky, okamžitě zakápni citronem (nezčerná).\n"
            "4. Cherry rajčata překroj napůl, okurku nakrájej na kolečka nebo půlměsíce.\n"
            "5. V malé misce smíchej olivový olej, lžičku citronu, špetku hořčice, sůl a pepř.\n"
            "6. Na misce (nebo rovnou v míse) rozlož zeleninu, přidej tuňáka, vejce a avokádo.\n"
            "7. Pokapej zálivkou a jemně promíchej, aby se avokádo nerozmáčklo."
        ),
        "tip": "Konzervovaný tuňák je jeden z nejlevnějších zdrojů kompletního proteinu.",
    },
    {
        "name":        "Caesar salát s kuřecím grilovaným",
        "kcal":        380,
        "protein":     34,
        "carbs":       14,
        "fat":         20,
        "time":        "20 min",
        "servings":    2,
        "category":    "Saláty",
        "tags":        ["proteinové", "klasika"],
        "ingredients": [
            "2 kuřecí prsa (cca 160 g)",
            "1 hlávka římského salátu",
            "30 g parmazánu",
            "2 lžíce Caesar dresinku",
            "krutony (volitelně)",
            "citrón, česnek, dijonská hořčice",
        ],
        "instructions": (
            "1. Kuřecí prsa potři olejem, solí, pepřem a prolisovaným česnekem. Griluj na grilu nebo pánvi 5–6 minut z každé strany, dokud není maso uvnitř bílé. Nechej 3 minuty odpočinout a pak nakrájej na plátky.\n"
            "2. Salát rozeběr na větší listy, propláchni studenou vodou a osuš (klíčové – zálivka ulpívá jen na suchých listech).\n"
            "3. Pokud děláš krutony domácí: nakrájej plátky chleba na kostičky, osmahni na suché pánvi s trochou česnekového oleje do zlatohněda.\n"
            "4. Do velké mísy dej salát, přidej dressing a jemně promíchej rukama.\n"
            "5. Přidej krutony, posypej nastrouhaným parmazánem.\n"
            "6. Navrch rozlož plátky kuřete, zakápni citronem a podávej ihned."
        ),
        "tip": "Římský salát má výjimečně tuhé listy, které dobře drží zálivku.",
    },
    {
        "name":        "Asijský salát s mrkví, zelím a arašídy",
        "kcal":        240,
        "protein":     9,
        "carbs":       28,
        "fat":         11,
        "time":        "15 min",
        "servings":    2,
        "category":    "Saláty",
        "tags":        ["vegan", "bez lepku", "antioxidanty"],
        "ingredients": [
            "¼ bílého zelí",
            "2 mrkve",
            "100 g edamame (vařené)",
            "50 g arašídů (nesolených)",
            "2 lžíce sójové omáčky (bez lepku)",
            "1 lžíce rýžového octa",
            "1 lžičce sezamového oleje",
            "zázvor, česnek, limetka",
        ],
        "instructions": (
            "1. Zelí nastrouhej na jemném struhadle nebo nakrájej na velmi tenké proužky. Stejně tak mrkev (nebo nastrouhej na hrubém struhadle).\n"
            "2. Zelí přirozeně prohněť se štipkou soli – pustí vodu a změkne. Po 5 minutách vymaž přebytečnou tekutinu.\n"
            "3. Připrav zálivku: smíchej sójovou omáčku, rýžový ocet, sezamový olej, nastrouhaný zázvor a prolisovaný česnek. Přidej limetkovou šťávu a podle chuti špetku cukru.\n"
            "4. V míse smíchej zelí, mrkev a edamame.\n"
            "5. Přelij zálivkou a promíchej. Nech 5 minut odstát.\n"
            "6. Při podávání posyp hrubě tlučenými arašídy a čerstvým koriandrem."
        ),
        "tip": "Zelí je bohaté na vitamín C a podporuje imunitu.",
    },
    {
        "name":        "Minestrone se zeleninou a těstovinami",
        "kcal":        195,
        "protein":     8,
        "carbs":       32,
        "fat":         4,
        "time":        "35 min",
        "servings":    4,
        "category":    "Polévky",
        "tags":        ["vegan", "vysokovláknité", "příprava do zásoby"],
        "ingredients": [
            "1 cibule",
            "2 mrkve",
            "2 stonky celeru",
            "1 cuketa",
            "400 g rajčat pelati (konzerva)",
            "400 g bílých fazolí (konzerva)",
            "80 g celozrnných těstovin (penne nebo fusilli)",
            "1 l zeleninového vývaru",
            "česnek, olivový olej, bazalka, tymián",
        ],
        "instructions": (
            "1. Cibuli, mrkev a celer nakrájej nadrobno (soffritto základ), česnek nasekej.\n"
            "2. V hrnci rozehřej 2 lžíce olivového oleje, osmahni soffritto 5 minut na středním plameni.\n"
            "3. Přidej česnek, jednu minutu osmahni.\n"
            "4. Přidej nakrájenou cuketu, restuj 2 minuty.\n"
            "5. Přidej pelati (rozmačkej je rukou přímo nad hrncem), fazole scezené a proplachnuté, vývar.\n"
            "6. Přiveď k varu, stáhni plamen a vař 15 minut.\n"
            "7. Přidej těstoviny a vař dle pokynů na obalu (obvykle 8–10 minut).\n"
            "8. Dochucuj solí, pepřem, bazalkou a tymiánem. Před podáváním pokap olivovým olejem."
        ),
        "tip": "Minestrone je skvělé jídlo do zásoby – druhý den je ještě lepší.",
    },
    {
        "name":        "Česnečka s vejcem",
        "kcal":        150,
        "protein":     8,
        "carbs":       16,
        "fat":         6,
        "time":        "15 min",
        "servings":    2,
        "category":    "Polévky",
        "tags":        ["česká klasika", "bez lepku", "imunita"],
        "ingredients": [
            "1 hlava česneku (8–10 stroužků)",
            "800 ml kuřecího nebo zeleninového vývaru",
            "2 vejce",
            "2 krajíce chleba",
            "1 lžíce sádla nebo másla",
            "sůl, pepř, kmín, majoránka",
        ],
        "instructions": (
            "1. Česnek oloupej a nakrájej na tenké plátky (nemusí být přesné).\n"
            "2. V hrnci rozehřej sádlo, přidej česnek a na mírném plameni osmahni do zlatova (3–4 minuty). Pozor – nesmí zhnědnout, jinak zhorkne.\n"
            "3. Zalijte vývar, přidej kmín a majoránku, přiveď k varu.\n"
            "4. Vař 8–10 minut na mírném plameni, dokud česnek nezměkne úplně.\n"
            "5. Chleba nakrájej na kostičky a opraž na suché pánvi nebo v troubě do křupavých krutonů.\n"
            "6. Polévku ochutnej a dochucuj solí a pepřem.\n"
            "7. Při podávání rozklepni do každé misky jedno syrové vejce a okamžitě přilij horkou polévku – vejce se svaří v misce."
        ),
        "tip": "Česnek obsahuje allicin s prokázanými antibakteriálními účinky.",
    },
    {
        "name":        "Proteinové palačinky s tvarohem",
        "kcal":        320,
        "protein":     28,
        "carbs":       38,
        "fat":         6,
        "time":        "20 min",
        "servings":    2,
        "category":    "Snídaně",
        "tags":        ["proteinové", "bez přidaného cukru"],
        "ingredients": [
            "200 g nízkotučného tvarohu",
            "3 vejce",
            "60 g ovesných vloček (rozemletých na mouku)",
            "1 lžičce prášku do pečiva",
            "špetka soli a vanilkového extraktu",
            "toping: čerstvé ovoce, med nebo sirup",
        ],
        "instructions": (
            "1. Ovesné vločky přeměl v mixéru nebo tyčovým mixérem na jemnou mouku.\n"
            "2. Do mísy přidej tvaroh, vejce, ovesnou mouku, prášek do pečiva, sůl a vanilku. Dobře promíchej – těsto bude husté.\n"
            "3. Nechej těsto 5 minut odležet – ovesná mouka navlhne a těsto zhoustne správně.\n"
            "4. Nepřilnavou pánev rozehřej na středním plameni, lehce pot\u0159i olejem.\n"
            "5. Nabírej lžíci těsta a vytaruj malé placičky (průměr 8–10 cm). Plačky jsou husté – pečou se pomaleji než čistá vajíčka.\n"
            "6. Peč 2–3 minuty, dokud okraje nezačnou tuhnout a povrch nebublat. Překlopení je o trpělivosti.\n"
            "7. Podávej s čerstvým ovocem nebo trochou medu."
        ),
        "tip": "Tyto palačinky mají 3× více bílkovin než tradiční recept.",
    },
    {
        "name":        "Banánové muffiny bez cukru",
        "kcal":        175,
        "protein":     5,
        "carbs":       30,
        "fat":         5,
        "time":        "30 min",
        "servings":    6,
        "category":    "Svačiny",
        "tags":        ["bez přidaného cukru", "vysokovláknité", "vegetariánské"],
        "ingredients": [
            "3 přezrálé banány",
            "2 vejce (nebo lněné vejce pro vegan verzi)",
            "150 g celozrnné mouky",
            "1 lžičce prášku do pečiva",
            "1 lžíce arašídového másla",
            "špetka soli a skořice",
            "volitelně: 50 g dark chocolate chips",
        ],
        "instructions": (
            "1. Troubu předehřej na 180 °C. Muffinovou formu vymaž nebo vlož papírové košíčky.\n"
            "2. Banány rozmačkej vidličkou na hladkou kaši – čím přezrálejší, tím sladší výsledek.\n"
            "3. Přidej vejce a arašídové máslo, metličkou promíchej do hladka.\n"
            "4. V druhé misce smíchej mouku, prášek do pečiva, sůl a skořici.\n"
            "5. Suché ingredience opatrně vmíchej do mokrých – míchej minimálně, jen do spojení. Přemíchané těsto = tuhé muffiny.\n"
            "6. Pokud používáš čokoládové kousky, jemně vmíchej.\n"
            "7. Rozděl těsto do 6 košíčků (cca ¾ plné) a peč 20–22 minut. Hotové jsou když špejle vyjde čistá.\n"
            "8. Nechej vychladnout alespoň 10 minut před konzumací."
        ),
        "tip": "Přezrálé banány jsou přirozeně sladké a nevyžadují přidaný cukr.",
    },
    {
        "name":        "Hummus domácí s mrkví a pita chlebem",
        "kcal":        220,
        "protein":     9,
        "carbs":       28,
        "fat":         8,
        "time":        "10 min",
        "servings":    4,
        "category":    "Svačiny",
        "tags":        ["vegan", "bez lepku možné", "vláknina"],
        "ingredients": [
            "400 g cizrny z konzervy",
            "2 lžíce tahini",
            "1 stroužek česneku",
            "3 lžíce olivového oleje",
            "šťáva z ½ citronu",
            "sůl, kmín, paprika na posypání",
            "mrkev na namáčení",
        ],
        "instructions": (
            "1. Cizrnu sceď – nálev zachovej, přidáme ho na úpravu konzistence.\n"
            "2. Cizrnu, tahini, výlisovaný česnek, citronovou šťávu a 2 lžíce olivového oleje vlož do mixéru nebo food processoru.\n"
            "3. Mixuj 1 minutu. Přidej 2–3 lžíce nálevu z cizrny (nebo ledové vody) a mixuj dalších 2 minuty – čím déle mixuješ, tím krémovější výsledek.\n"
            "4. Ochutnaj a uprav sůl a citron. Pokud chceš více česnekové chuti, přidej.\n"
            "5. Přendej do misky, lžící vytvoř mělkou jamku uprostřed a přelij zbylým olivovým olejem.\n"
            "6. Posypej mletou paprikou a kmínem.\n"
            "7. Podávej s mrkví nakrájenou na tyčky a plátky pita chleba."
        ),
        "tip": "Tahini (sezamová pasta) je výborný zdroj vápníku a zinku.",
    },
    {
        "name":        "Proteinový hrnek s tvarohem a ovocem",
        "kcal":        190,
        "protein":     20,
        "carbs":       22,
        "fat":         2,
        "time":        "3 min",
        "servings":    1,
        "category":    "Svačiny",
        "tags":        ["proteinové", "bez přidaného cukru", "rychlá příprava"],
        "ingredients": [
            "200 g nízkotučného tvarohu",
            "100 g sezonního ovoce",
            "1 lžičce vanilkového extraktu",
            "volitelně: lžíce medu nebo javorového sirupu",
        ],
        "instructions": (
            "1. Tvaroh vyndej z lednice 5 minut dopředu – lépe se mixuje když není ledový.\n"
            "2. Přidej vanilkový extrakt a tyčovým mixerem přešlehej do hladka (nebo zpracuj vidličkou pro hrubší texturu).\n"
            "3. Ovoce nakrájej na sousto: jahody na čtvrtiny, borůvky celé, broskev na plátky.\n"
            "4. Tvaroh přendej do misky nebo sklenice, navrch rozlož ovoce.\n"
            "5. Pokud chceš sladší, zakápni medem."
        ),
        "tip": "Tvaroh je jeden z nejbohatších zdrojů kaseinu – ideální svačina před spánkem.",
    },
    {
        "name":        "Pečené batáty plněné fazolemi a salantou",
        "kcal":        370,
        "protein":     14,
        "carbs":       68,
        "fat":         5,
        "time":        "55 min",
        "servings":    2,
        "category":    "Hlavní jídla",
        "tags":        ["vegan", "bez lepku", "vysokovláknité"],
        "ingredients": [
            "2 střední batáty (sladké brambory)",
            "400 g černých fazolí (konzerva)",
            "100 g kukuřice (konzerva)",
            "½ červené cibule",
            "1 avokádo",
            "limetka, koriandr, kmín, chilli",
        ],
        "instructions": (
            "1. Troubu předehřej na 200 °C. Batáty propíchej vidličkou 10× ze všech stran.\n"
            "2. Polož batáty přímo na rošt (nebo na plech) a peč 45–50 minut, dokud nejsou úplně měkké – zkontroluj špejlí.\n"
            "3. 10 minut před koncem pečení připrav náplň: cibuli nakrájej nadrobno, fazole sceď a prohřej na pánvi s kmínem a chilli.\n"
            "4. Avokádo rozmačkej s limetkovou šťávou na guacamole.\n"
            "5. Upečené batáty překroj napůl a vidličkou trochu rozmačkej dužinu uvnitř.\n"
            "6. Plň fazolemi, kukuřicí a cibulí.\n"
            "7. Navrch dej lžíci guacamole a posyp čerstvým koriandrem."
        ),
        "tip": "Batáty mají nižší glykemický index než brambory díky vláknině.",
    },
    {
        "name":        "Krůtí masové koule s cuketovými nudlemi",
        "kcal":        340,
        "protein":     32,
        "carbs":       14,
        "fat":         16,
        "time":        "30 min",
        "servings":    2,
        "category":    "Hlavní jídla",
        "tags":        ["bez lepku", "proteinové", "nízkosacharidové"],
        "ingredients": [
            "300 g mletého krůtího masa",
            "2 cukety (na spiralizování)",
            "1 vejce",
            "2 lžíce strouhanky (nebo ovesné mouky)",
            "2 stroužky česneku",
            "½ cibule",
            "250 ml rajčatové passaty",
            "bazalka, oregano, sůl, pepř",
        ],
        "instructions": (
            "1. Smíchej mleté maso, vejce, strouhanku, prolisovaný česnek, jemně nakrájenou cibuli, sůl a pepř. Formuj mokrýma rukama kuličky (průměr 3 cm).\n"
            "2. Na pánvi rozehřej olej, opékej kuličky ze všech stran 6–8 minut do zlatovohněda.\n"
            "3. Přidej passatu, oregano a bazalku. Stáhni plamen a vař přikryté 10 minut.\n"
            "4. Cukety spiralizuj na nudle (nebo nastrouhej na hrubém struhadle na dlouhé proužky).\n"
            "5. Cuketové nudle osolí a nechej 5 minut – pustí vodu. Pak vymačkej přebytečnou vlhkost.\n"
            "6. Na suché pánvi osmaž cuketové nudle 2–3 minuty – chceme aby zůstaly al dente.\n"
            "7. Podávej masové kuličky s omáčkou na cuketových nudlích."
        ),
        "tip": "Cuketové nudle mají 5× méně kalorií než klasické těstoviny.",
    },
    {
        "name":        "Polévka z červené čočky s kokosovým mlékem",
        "kcal":        270,
        "protein":     14,
        "carbs":       38,
        "fat":         8,
        "time":        "25 min",
        "servings":    3,
        "category":    "Polévky",
        "tags":        ["vegan", "bez lepku", "proteinové"],
        "ingredients": [
            "200 g červené čočky",
            "400 ml kokosového mléka (light)",
            "400 ml zeleninového vývaru",
            "1 cibule",
            "2 stroužky česneku",
            "1 lžička kurkumy",
            "1 lžička koriandru",
            "½ lžičky chilli",
            "citron, čerstvý koriandr",
        ],
        "instructions": (
            "1. Čočku propláchni v sítku pod studenou vodou.\n"
            "2. V hrnci osmahni nadrobno nakrájenou cibuli na oleji 3 minuty. Přidej prolisovaný česnek a suché koření – 30 sekund míchej, až se koření rozvoní.\n"
            "3. Přidej čočku, zalij vývar a kokosové mléko. Přiveď k varu.\n"
            "4. Snižpi plamen a vař přikryté 15–18 minut, dokud čočka úplně nezměkne a nerozpadne.\n"
            "5. Polévku rozmixuj tyčovým mixérem do hladka (nebo nechej částečně hrubou podle chuti).\n"
            "6. Dochucuj solí, citronem a chilli. Přidej trochu vývaru pokud je příliš hustá.\n"
            "7. Podávej posypanou čerstvým koriandrem a zakápenou citronem."
        ),
        "tip": "Kurkuma má silné protizánětlivé účinky díky látce kurkuminu.",
    },
    {
        "name":        "Kaše z červené čočky (dhal)",
        "kcal":        290,
        "protein":     18,
        "carbs":       44,
        "fat":         6,
        "time":        "30 min",
        "servings":    3,
        "category":    "Hlavní jídla",
        "tags":        ["vegan", "bez lepku", "proteinové"],
        "ingredients": [
            "250 g červené čočky",
            "1 cibule",
            "3 stroužky česneku",
            "400 ml konzervovaných rajčat",
            "200 ml kokosového mléka",
            "1 lžíce ghee nebo kokosového oleje",
            "1 lžička garam masala",
            "1 lžička kurkumy",
            "čerstvý koriandr, rýže na podávání",
        ],
        "instructions": (
            "1. Čočku propláchni, zalij vodou a nechej 20 minut namočit (zkrátí dobu vaření).\n"
            "2. V hrnci s těžkým dnem rozehřej ghee na středním plameni. Osmahni nadrobno nakrájenou cibuli 5 minut.\n"
            "3. Přidej prolisovaný česnek, garam masalu a kurkumu – míchej 1 minutu dokud se koření nerozvoní.\n"
            "4. Přidej scezenou čočku, rajčata (rozmačkej je v hrnci) a kokosové mléko.\n"
            "5. Přiveď k varu, stáhni plamen a vař přikryté 20 minut, dokud čočka nezměkne úplně. Občas promíchej.\n"
            "6. Pokud je dhal příliš hustý, přidej trochu vody a prohřej.\n"
            "7. Dochucuj solí a podávej s rýží a čerstvým koriandrem."
        ),
        "tip": "Dhal je jedním z nejúspornějších a výživnostně nejbohatších jídel světa.",
    },
]


def get_healthy_recipes(count: int = 3) -> List[Dict]:
    """Vrátí `count` náhodně vybraných zdravých receptů – nejprve z DB, jinak statický katalog."""
    try:
        from utils.json_db import get_healthy_recipes_db
        results = get_healthy_recipes_db(count)
        if results:
            return results
    except Exception:
        pass
    pool = list(_HEALTHY_RECIPES)
    random.shuffle(pool)
    return pool[:count]


def get_all_recipes() -> List[Dict]:
    """Vrátí celý katalog zdravých receptů – nejprve z DB, jinak statický katalog."""
    try:
        from utils.json_db import get_all_recipes_db
        results = get_all_recipes_db()
        if results:
            return results
    except Exception:
        pass
    return list(_HEALTHY_RECIPES)
