/**
 * shop_emoji.js – Ürün adından emoji/ikon belirleyen akıllı eşleştirici
 * Desteklenen diller: Türkçe · English · Deutsch
 * ~110 ürün grubu · 400+ keyword
 *
 * Eşleştirme mantığı (sıralı öncelik):
 *   1. Tam cümle eşleşmesi  ("yeşil elma" → 🍏)
 *   2. Tam kelime eşleşmesi  ("domates" kelimesi geçiyor mu?)
 *   3. Kelime-başı eşleşmesi ("kıymalı" → kıyma* → 🥩)
 *   4. Fallback → ilk büyük harf (mavi kart)
 *
 * Bu yaklaşım substring tuzaklarını engeller:
 *   "su" ≠ fa*su*lye · "kola" ≠ çi*kola*ta · "balık" ≠ başka şey
 */

(function () {
  'use strict';

  // ─── Normalize ────────────────────────────────────────────────────────────
  function norm(s) {
    return String(s || '')
      .toLowerCase()
      .replace(/ğ/g, 'g').replace(/ü/g, 'u').replace(/ş/g, 's')
      .replace(/ı/g, 'i').replace(/ö/g, 'o').replace(/ç/g, 'c')
      .replace(/ä/g, 'a').replace(/ö/g, 'o').replace(/ü/g, 'u')
      .replace(/ß/g, 'ss')
      .trim();
  }

  // Girilen metni kelimelere böl (birden fazla boşluk, tire de ayırıcı)
  function words(s) {
    return norm(s).split(/[\s\-\/,]+/).filter(Boolean);
  }

  // ─── Ürün Grubu Tanımları ─────────────────────────────────────────────────
  // Her grup: { emoji, hue (fallback renk), exact[], word[], prefix[] }
  //   exact   → tam string eşleşmesi (norm edilmiş)
  //   word    → herhangi bir KElIME tam eşleşmesi
  //   prefix  → herhangi bir KELİME bu prefix ile başlıyorsa eşleşir
  //             ("kıymalı" → prefix "kiyma" ile başlar ✓)
  const GROUPS = [

    // ══════════════════ MEYVE ══════════════════
    { emoji:'🍎', hue:0,
      exact:['elma','apple','apfel'],
      word:['elma','apple','apfel','aeble'],
      prefix:['kirmizi elma','red apple','roter apfel'] },

    { emoji:'🍏', hue:100,
      exact:['yesil elma','green apple','gruner apfel','granny smith'],
      word:[],
      prefix:['yesil elma','green apple','grune'] },

    { emoji:'🍊', hue:30,
      exact:['portakal','mandalina','orange','mandarine'],
      word:['portakal','mandalina','orange','mandarine','clementine','satsuma'],
      prefix:['portakal','mandal','orange','mandarin'] },

    { emoji:'🍋', hue:50,
      exact:['limon','lemon','zitrone'],
      word:['limon','lemon','zitrone','limonata'],
      prefix:['limon','lemon','zitron'] },

    { emoji:'🍇', hue:270,
      exact:['uzum','grape','traube','weintraube'],
      word:['uzum','grape','traube','weintraube'],
      prefix:['uzum','grape','traub'] },

    { emoji:'🍓', hue:350,
      exact:['cilek','strawberry','erdbeere'],
      word:['cilek','strawberry','erdbeere'],
      prefix:['cilek','strawberr','erdbeer'] },

    { emoji:'🍒', hue:340,
      exact:['kiraz','visne','cherry','kirsche'],
      word:['kiraz','visne','cherry','kirsche'],
      prefix:['kiraz','visne','cherr','kirsch'] },

    { emoji:'🍑', hue:25,
      exact:['seftali','peach','pfirsich'],
      word:['seftali','peach','pfirsich'],
      prefix:['seftal','peach','pfirs'] },

    { emoji:'🥭', hue:40,
      exact:['mango','mango'],
      word:['mango'],
      prefix:['mango'] },

    { emoji:'🍍', hue:55,
      exact:['ananas','pineapple','ananas'],
      word:['ananas','pineapple'],
      prefix:['ananas','pineappl'] },

    { emoji:'🍌', hue:55,
      exact:['muz','banana','banane'],
      word:['muz','banana','banane'],
      prefix:['muz','banan'] },

    { emoji:'🍉', hue:350,
      exact:['karpuz','watermelon','wassermelone'],
      word:['karpuz','watermelon','wassermelone'],
      prefix:['karpuz','watermel','wassermel'] },

    { emoji:'🍈', hue:100,
      exact:['kavun','melon','melone'],
      word:['kavun','melon','melone'],
      prefix:['kavun','melon'] },

    { emoji:'🍐', hue:80,
      exact:['armut','pear','birne'],
      word:['armut','pear','birne'],
      prefix:['armut','pear','birn'] },

    { emoji:'🫐', hue:240,
      exact:['yaban mersini','blueberry','heidelbeere','blaubeere'],
      word:['mersini','blueberry','heidelbeere','blaubeere'],
      prefix:['mersin','blueberr','heidelbeer','blaubeer'] },

    { emoji:'🥝', hue:100,
      exact:['kivi','kiwi'],
      word:['kivi','kiwi'],
      prefix:['kivi','kiwi'] },

    { emoji:'🍅', hue:10,
      exact:['domates','tomato','tomate'],
      word:['domates','tomato','tomate'],
      prefix:['domates','tomato','tomat'] },

    { emoji:'🥑', hue:120,
      exact:['avokado','avocado'],
      word:['avokado','avocado'],
      prefix:['avokad','avocad'] },

    { emoji:'🍋‍🟩', hue:90,
      exact:['misket limonu','lime'],
      word:['lime','misket'],
      prefix:['lime'] },

    // ══════════════════ SEBZE ══════════════════
    { emoji:'🥕', hue:30,
      exact:['havuc','carrot','karotte','mohre'],
      word:['havuc','carrot','karotte','mohre'],
      prefix:['havuc','carrot','karot','mohr'] },

    { emoji:'🥦', hue:120,
      exact:['brokoli','broccoli','brokkoli'],
      word:['brokoli','broccoli','brokkoli'],
      prefix:['brokol','broccol','brokkol'] },

    { emoji:'🥬', hue:130,
      exact:['marul','iceberg','lahana','lettuce','salat','kopfsalat'],
      word:['marul','iceberg','lahana','lettuce','salat','kopfsalat'],
      prefix:['marul','iceberg','lahan','lettuc','salat','kopfsal'] },

    { emoji:'🌽', hue:55,
      exact:['misir','corn','mais'],
      word:['misir','corn','mais'],
      prefix:['misir','corn','mais'] },

    { emoji:'🫑', hue:120,
      exact:['biber','pepper','paprika'],
      word:['biber','pepper','paprika'],
      prefix:['biber','pepper','paprik'] },

    { emoji:'🧅', hue:40,
      exact:['sogan','onion','zwiebel'],
      word:['sogan','onion','zwiebel'],
      prefix:['sogan','onion','zwiebel'] },

    { emoji:'🧄', hue:45,
      exact:['sarimsak','garlic','knoblauch'],
      word:['sarimsak','garlic','knoblauch'],
      prefix:['sarimsa','garlic','knoblau'] },

    { emoji:'🥔', hue:40,
      exact:['patates','potato','kartoffel'],
      word:['patates','potato','kartoffel'],
      prefix:['patat','potato','kartof'] },

    { emoji:'🍆', hue:280,
      exact:['patlican','eggplant','aubergine'],
      word:['patlican','eggplant','aubergine'],
      prefix:['patlican','eggplant','aubergin'] },

    { emoji:'🥒', hue:110,
      exact:['salatalik','cucumber','gurke'],
      word:['salatalik','cucumber','gurke','acur'],
      prefix:['salatat','cucumb','gurke','acur'] },

    { emoji:'🫛', hue:120,
      exact:['bezelye','pea','erbse'],
      word:['bezelye','pea','erbse'],
      prefix:['bezelyе','erbse'] },

    { emoji:'🫘', hue:120,
      exact:['fasulye','baklagil','bean','bohne','nohut','mercimek','lentil','linse','chickpea','kichererbse'],
      word:['fasulye','bean','bohne','nohut','mercimek','lentil','linse','kichererbse'],
      prefix:['fasulyе','fasul','bean','bohn','nohut','mercim','lentil','linse','kicher'] },

    { emoji:'🥜', hue:40,
      exact:['yer fistigi','peanut','erdnuss'],
      word:['fistigi','peanut','erdnuss','fistik'],
      prefix:['fistik','peanut','erdnuss'] },

    { emoji:'🌶️', hue:0,
      exact:['aci biber','chili','cayenne','jalapeno'],
      word:['chili','cayenne','jalapeno'],
      prefix:['chili','cayenn','jalapen'] },

    { emoji:'🧆', hue:40,
      exact:['mantar','mushroom','pilz','champignon'],
      word:['mantar','mushroom','pilz','champignon'],
      prefix:['mantar','mushroom','pilz','champign'] },

    { emoji:'🥗', hue:120,
      exact:['roka','ispanak','spinach','spinat'],
      word:['roka','ispanak','spinach','spinat'],
      prefix:['roka','ispanak','spinach','spinat'] },

    // ══════════════════ ET & TAVUK ══════════════════
    { emoji:'🥩', hue:0,
      exact:['et','kiyma','biftek','steak','bonfile','kusbasi','antrikot','pirzola','meat','fleisch','rinderhack','hackfleisch'],
      word:['et','kiyma','biftek','steak','bonfile','kusbasi','antrikot','pirzola','meat','fleisch','rinderhack','hackfleisch'],
      prefix:['kiyma','biftek','bonfile','kusba','antrikot','pirzola','steakfl','hackfl','rinderha'] },

    { emoji:'🍗', hue:40,
      exact:['tavuk','chicken','huhn','hahnchen'],
      word:['tavuk','chicken','huhn','hahnchen'],
      prefix:['tavuk','chicken','huhn','hahnch'] },

    { emoji:'🥓', hue:10,
      exact:['sucuk','sosis','salam','bacon','speck','wurst','pastirma'],
      word:['sucuk','sosis','salam','bacon','speck','wurst','pastirma','wurstchen'],
      prefix:['sucuk','sosis','salam','bacon','speck','wurst','pastirm'] },

    { emoji:'🍖', hue:30,
      exact:['kuzu','lamb','lamm','koyun'],
      word:['kuzu','lamb','lamm','koyun'],
      prefix:['kuzu','lamb','lamm','koyun'] },

    { emoji:'🐟', hue:200,
      exact:['balik','fish','fisch'],
      word:['balik','fish','fisch'],
      prefix:['balik','salmon','alabalik','uskumru','hamsi','fisch'] },

    { emoji:'🍤', hue:30,
      exact:['karides','shrimp','garnele'],
      word:['karides','shrimp','garnele'],
      prefix:['karides','shrimp','garnel'] },

    { emoji:'🦑', hue:350,
      exact:['ahtapot','kalamar','octopus','squid'],
      word:['ahtapot','kalamar','octopus','squid'],
      prefix:['ahtap','kalama','octop','squid'] },

    // ══════════════════ SÜT ÜRÜNLERİ ══════════════════
    { emoji:'🥛', hue:210,
      exact:['sut','milk','milch'],
      word:['sut','milk','milch'],
      prefix:['sut','milk','milch'] },

    { emoji:'🧀', hue:50,
      exact:['peynir','cheese','kase'],
      word:['peynir','cheese','kase','mozarella','cheddar','gouda','parmesan','beyaz peynir'],
      prefix:['peynir','chees','kase','mozar','cheddar','gouda','parmes'] },

    { emoji:'🧈', hue:55,
      exact:['tereyagi','butter','margarin'],
      word:['tereyagi','butter','margarin'],
      prefix:['tereyag','tereyagi','butter','buttr','marga'] },

    { emoji:'🥚', hue:50,
      exact:['yumurta','egg','ei'],
      word:['yumurta','egg','ei','eier'],
      prefix:['yumurta','egg','ei'] },

    { emoji:'🍦', hue:40,
      exact:['dondurma','ice cream','eis'],
      word:['dondurma','eis','icecream'],
      prefix:['dondurma','icecream'] },

    { emoji:'🥛', hue:200,
      exact:['yogurt','ayran','kefir'],
      word:['yogurt','ayran','kefir'],
      prefix:['yogurt','ayran','kefir'] },

    { emoji:'🍶', hue:30,
      exact:['krema','cream','sahne','sour cream','eksi krema'],
      word:['krema','cream','sahne'],
      prefix:['krema','cream','sahne'] },

    // ══════════════════ EKMEK & UNLU ══════════════════
    { emoji:'🍞', hue:35,
      exact:['ekmek','bread','brot','sandvic','toast'],
      word:['ekmek','bread','brot','toast','sandvic','bagel','croissant'],
      prefix:['ekmek','bread','brot','toast','sandvi','croiss'] },

    { emoji:'🥐', hue:35,
      exact:['kruvasan','croissant'],
      word:['kruvasan','croissant'],
      prefix:['kruvas','croiss'] },

    { emoji:'🥖', hue:40,
      exact:['baget','baguette','simit'],
      word:['baget','baguette','simit'],
      prefix:['baget','baguet','simit'] },

    { emoji:'🧁', hue:320,
      exact:['kek','muffin','cupcake','pasta','cake'],
      word:['kek','muffin','cupcake','pasta','cake','torte'],
      prefix:['kek','muffin','cupcak','pastasi','torte'] },

    { emoji:'🥞', hue:40,
      exact:['gozleme','pancake','pfannkuchen','galeta'],
      word:['gozleme','pancake','pfannkuchen','galeta'],
      prefix:['gozlem','pancak','pfannku','galet'] },

    { emoji:'🍪', hue:35,
      exact:['biskuvi','cookie','keks','bisküvi'],
      word:['biskuvi','cookie','keks'],
      prefix:['biskuvi','cook','keks'] },

    { emoji:'🥨', hue:40,
      exact:['kraker','cracker','brezel'],
      word:['kraker','cracker','brezel'],
      prefix:['kraker','cracker','brezel'] },

    // ══════════════════ IÇECEK ══════════════════
    { emoji:'💧', hue:200,
      exact:['su','water','wasser'],
      word:['su','water','wasser'],
      prefix:[] },   // prefix yok → "su" sadece tam kelime olarak eşleşir

    { emoji:'🧃', hue:40,
      exact:['meyve suyu','juice','saft'],
      word:['suyu','juice','saft','meyve suyu'],
      prefix:['meyvesuyu','juice','saft'] },

    { emoji:'☕', hue:30,
      exact:['kahve','coffee','kaffee'],
      word:['kahve','coffee','kaffee','espresso','latte','cappuccino','americano'],
      prefix:['kahve','coffee','kaffee','espresso','latte','cappucc','americ'] },

    { emoji:'🍵', hue:120,
      exact:['cay','tea','tee'],
      word:['cay','tea','tee','bitki cayi','ihlamur','nane','papatya'],
      prefix:['cay','tea','tee','ihlamur','nane','papaty'] },

    { emoji:'🥤', hue:350,
      exact:['kola','cola','pepsi','fanta','sprite'],
      word:['kola','cola','pepsi','fanta','sprite'],
      prefix:['pepsi','fanta','sprite'] },
      // NOT: "kola" sadece tam kelime eşleşir → "çikolata" eşleşmez

    { emoji:'🍺', hue:50,
      exact:['bira','beer','bier'],
      word:['bira','beer','bier'],
      prefix:['bira','beer','bier'] },

    { emoji:'🍷', hue:310,
      exact:['sarap','wine','wein'],
      word:['sarap','wine','wein','reze','merlot','cabernet'],
      prefix:['sarap','wine','wein'] },

    { emoji:'🥂', hue:55,
      exact:['sampanya','champagne','sekt'],
      word:['sampanya','champagne','sekt','prosecco'],
      prefix:['sampany','champagn','prosec'] },

    { emoji:'🧊', hue:200,
      exact:['buz','ice','eis cubes'],
      word:['buz'],
      prefix:['buz'] },

    { emoji:'🥛', hue:60,
      exact:['soya sutu','almond milk','oat milk','hafermilch','mandelmilch','sojamilch'],
      word:['soya','hafermilch','mandelmilch','sojamilch'],
      prefix:['soya','hafer','mandel','sojam'] },

    // ══════════════════ ATISTIRMALIK ══════════════════
    { emoji:'🍫', hue:30,
      exact:['cikolata','chocolate','schokolade'],
      word:['cikolata','chocolate','schokolade','kakao'],
      prefix:['cikolata','chocolat','schokolad','kakao'] },

    { emoji:'🍬', hue:320,
      exact:['seker','candy','bonbon','sucker'],
      word:['seker','candy','bonbon','lokum'],
      prefix:['seker','candy','bonbon','lokum'] },

    { emoji:'🍭', hue:310,
      exact:['lolipop','lollipop','lutscher'],
      word:['lolipop','lollipop','lutscher'],
      prefix:['lolip','lutscher'] },

    { emoji:'🍡', hue:350,
      exact:['gummy','jellibon','gummibaren','haribo'],
      word:['jellibon','gummibaren','haribo','gummy'],
      prefix:['jellibon','gummib','haribo'] },

    { emoji:'🥜', hue:45,
      exact:['cips','chips','fistik','nuts'],
      word:['cips','chips','fistik','nuts','leblebi','kavurga'],
      prefix:['cips','chips','fistik','nuts','leblebi','kavur'] },

    { emoji:'🍿', hue:50,
      exact:['patlamis misir','popcorn'],
      word:['popcorn'],
      prefix:['popcorn'] },

    // ══════════════════ TAHIL & KİLER ══════════════════
    { emoji:'🌾', hue:50,
      exact:['un','flour','mehl'],
      word:['un','flour','mehl'],
      prefix:['buğday unu','corn flour','weizenmehl'] },

    { emoji:'🍚', hue:50,
      exact:['pirinc','rice','reis'],
      word:['pirinc','rice','reis'],
      prefix:['pirinc','rice','reis'] },

    { emoji:'🍝', hue:50,
      exact:['makarna','pasta','nudel','spaghetti','penne','fusilli'],
      word:['makarna','nudel','spaghetti','penne','fusilli','eriste','noodle'],
      prefix:['makarna','nudel','spaghett','penne','fusilli','noodle'] },

    { emoji:'🥣', hue:45,
      exact:['yulaf','oatmeal','oat','haferflocken','granola','musli'],
      word:['yulaf','oatmeal','haferflocken','granola','musli'],
      prefix:['yulaf','oatmeal','haferfl','granola','musli'] },

    { emoji:'🍯', hue:45,
      exact:['bal','honey','honig'],
      word:['bal','honey','honig'],
      prefix:['bal','honey','honig'] },

    { emoji:'🧂', hue:200,
      exact:['tuz','salt','salz'],
      word:['tuz','salt','salz'],
      prefix:['tuz','salt','salz'] },

    { emoji:'🌿', hue:120,
      exact:['karabiber','biber','pepper','pfeffer','kimyon','bahar'],
      word:['karabiber','kimyon','bahar','pfeffer','paprika tozu','zerdeçal'],
      prefix:['karabiber','kimyon','pfeffer','zerdet','paprika tozu'] },

    { emoji:'🫙', hue:50,
      exact:['zeytinyagi','olive oil','olivenöl','yag','oil','ol'],
      word:['zeytinyagi','olivenol','ayicicek yagi','sunflower oil'],
      prefix:['zeytinyag','olivenol','ayicic','sunflow'] },

    { emoji:'🍶', hue:40,
      exact:['sirke','vinegar','essig'],
      word:['sirke','vinegar','essig'],
      prefix:['sirke','vinegar','essig'] },

    { emoji:'🫕', hue:30,
      exact:['salca','sauce','sosse','ketchup','mayonez','mustard','hardal'],
      word:['salca','ketchup','mayonez','mustard','hardal','sosse','pesto'],
      prefix:['salca','ketchup','mayonez','mustard','hardal','sosse','pesto'] },

    // ══════════════════ DONDURULMUŞ ══════════════════
    { emoji:'🧊', hue:190,
      exact:['dondurulmus','frozen','tiefkuhl','gefroren'],
      word:['dondurulmus','frozen','tiefkuhl'],
      prefix:['dondurulm','frozen','tiefkuhl','gefror'] },

    // ══════════════════ TEMİZLİK ══════════════════
    { emoji:'🧴', hue:200,
      exact:['sabun','sıvı sabun','soap','seife','duş jeli','shower gel'],
      word:['sabun','soap','seife','sampuan','shampoo','kondisyoner','conditioner'],
      prefix:['sabun','soap','seife','sampuan','shampoo','kondisy','condition'] },

    { emoji:'🪥', hue:210,
      exact:['dis macunu','dis fircasi','toothpaste','zahnpasta','toothbrush','zahnburste'],
      word:['macunu','fircasi','toothpaste','zahnpasta','toothbrush','zahnburste'],
      prefix:['macun','firca','toothp','zahnp','toothbr','zahnb'] },

    { emoji:'🧻', hue:50,
      exact:['tuvalet kagidi','toilet paper','toilettenpapier','pecete','kagit havlu'],
      word:['tuvalet','toilettenpapier','pecete','kagit havlu'],
      prefix:['tuvalet','toilettenpap','pecete','kagit'] },

    { emoji:'🧹', hue:45,
      exact:['supurge','broom','besen'],
      word:['supurge','broom','besen'],
      prefix:['supurge','broom','besen'] },

    { emoji:'🪣', hue:200,
      exact:['kovа','bucket','eimer'],
      word:['kova','bucket','eimer'],
      prefix:['kova','bucket','eimer'] },

    { emoji:'🧼', hue:200,
      exact:['deterjan','laundry','waschmittel','bulasik','dishwash','gululu'],
      word:['deterjan','waschmittel','bulasik','dishwash'],
      prefix:['deterjan','waschmit','bulasik','dishwash'] },

    { emoji:'🫧', hue:200,
      exact:['camsil','cam temizleyici','glasreiniger','windex','cif'],
      word:['camsil','glasreiniger'],
      prefix:['camsil','glasr'] },

    { emoji:'🧽', hue:50,
      exact:['sunger','sponce','schwamm'],
      word:['sunger','sponge','schwamm'],
      prefix:['sunger','sponge','schwamm'] },

    // ══════════════════ KİŞİSEL BAKIM ══════════════════
    { emoji:'🧴', hue:320,
      exact:['losyon','lotion','krem','cream','feuchtigkeitscreme','deodorant','deo'],
      word:['losyon','lotion','krem','feuchtigkeitscreme','deodorant','deo'],
      prefix:['losyon','lotion','krem','feuchtigk','deodoran','deo'] },

    { emoji:'💊', hue:0,
      exact:['ilac','medicine','medikament','vitamin','aspirin','agri kesici'],
      word:['ilac','medicine','medikament','vitamin','aspirin','ibuprofen','parol'],
      prefix:['ilac','medic','medikam','vitamin','aspirin','ibuprofen','parol'] },

    { emoji:'🩹', hue:10,
      exact:['yara bandi','plaster','pflaster'],
      word:['yara bandi','plaster','pflaster'],
      prefix:['yara','plaster','pflaster'] },

    { emoji:'🪒', hue:200,
      exact:['tras','razor','rasierer','tras kopugu'],
      word:['tras','razor','rasierer'],
      prefix:['tras','razor','rasier'] },

    { emoji:'🪮', hue:200,
      exact:['tarak','comb','kamm'],
      word:['tarak','comb','kamm'],
      prefix:['tarak','comb','kamm'] },

    // ══════════════════ BEBEK ÜRÜNLERİ ══════════════════
    { emoji:'🍼', hue:50,
      exact:['bebek sutu','mama','babymilch','babynahrung','biberon'],
      word:['mama','babymilch','babynahrung','biberon'],
      prefix:['mama','babym','babynahrung','biberon'] },

    { emoji:'🧷', hue:210,
      exact:['bez','windel','diaper'],
      word:['bez','windel','diaper','pampers'],
      prefix:['windel','diaper','pampers'] },

    { emoji:'🧸', hue:40,
      exact:['bebek'],
      word:['bebek'],
      prefix:[] },

    // ══════════════════ KATEGORİ GENELİ ══════════════════
    { emoji:'🥫', hue:50,
      exact:['konserve','canned','dose','konserveler'],
      word:['konserve','canned','dose'],
      prefix:['konserve','canned','dose'] },

    { emoji:'🫙', hue:40,
      exact:['recel','jam','marmelade','nutella'],
      word:['recel','jam','marmelade','nutella'],
      prefix:['recel','jam','marmelad','nutella'] },

    { emoji:'🥐', hue:40,
      exact:['poğaça','acma','simite'],
      word:['pogaca','acma'],
      prefix:['pogaca','acma'] },

    { emoji:'🧆', hue:50,
      exact:['ceviz','walnut','walnuss','badem','almond','mandel','findik','hazelnut','haselnuss'],
      word:['ceviz','walnut','walnuss','badem','almond','mandel','findik','hazelnut','haselnuss'],
      prefix:['ceviz','walnut','walnus','badem','almond','mandel','findik','hazelnut','haselnus'] },

    { emoji:'🌱', hue:120,
      exact:['maydanoz','dereotu','nane','reyhan','fesligen','parsley','basil','thyme','kekik'],
      word:['maydanoz','dereotu','nane','reyhan','fesligen','parsley','basil','thyme','kekik'],
      prefix:['maydanoz','dereotu','nane','reyhan','fesligen','parsley','basil','thyme','kekik'] },

    { emoji:'🍱', hue:50,
      exact:['hazir yemek','hazir','ready meal','fertiggericht'],
      word:['hazir yemek','fertiggericht'],
      prefix:['hazir yem','fertigg'] },

    { emoji:'🛒', hue:200,
      exact:['diger','other','sonstiges'],
      word:[],
      prefix:[] },
  ];

  // ─── Ana eşleştirici ──────────────────────────────────────────────────────
  function resolveEmoji(name) {
    const raw      = String(name || '').trim();
    const normFull = norm(raw);
    const ws       = words(raw);

    for (const g of GROUPS) {
      // 1. Tam cümle (exact)
      if (g.exact.some(k => norm(k) === normFull)) return g.emoji;
    }

    for (const g of GROUPS) {
      // 2. Herhangi bir kelime tam eşleşmesi
      if (g.word.some(k => ws.includes(norm(k)))) return g.emoji;
    }

    for (const g of GROUPS) {
      // 3. Herhangi bir kelime, prefix ile başlıyor mu?
      if (g.prefix.some(k => ws.some(w => w.startsWith(norm(k))))) return g.emoji;
    }

    return null; // emoji bulunamadı → fallback
  }

  // ─── Kart HTML üreteci ────────────────────────────────────────────────────
  const FALLBACK_COLORS = [
    '#3b82f6','#8b5cf6','#ec4899','#f59e0b','#10b981',
    '#ef4444','#06b6d4','#84cc16','#f97316','#6366f1',
  ];

  function cardHTML(name) {
    const emoji = resolveEmoji(name);
    const label = (name || '?').trim();

    if (emoji) {
      return `<div style="
          width:56px;height:56px;border-radius:14px;
          background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.12);
          display:flex;flex-direction:column;align-items:center;justify-content:center;
          flex-shrink:0;gap:1px;overflow:hidden;
          box-shadow:0 2px 8px rgba(0,0,0,.25);">
        <span style="font-size:26px;line-height:1;">${emoji}</span>
      </div>`;
    }

    // Fallback: ilk harf + renk
    const initial = label[0].toUpperCase();
    const color   = FALLBACK_COLORS[label.charCodeAt(0) % FALLBACK_COLORS.length];
    return `<div style="
        width:56px;height:56px;border-radius:14px;
        background:${color};
        display:flex;align-items:center;justify-content:center;
        flex-shrink:0;font-size:22px;font-weight:800;color:#fff;
        box-shadow:0 2px 8px rgba(0,0,0,.25);">
      ${initial}
    </div>`;
  }

  // ─── Public API ───────────────────────────────────────────────────────────
  window.ShopEmoji = { resolveEmoji, cardHTML };
})();
