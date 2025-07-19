extends Control

# Game state variables
var ethics: int = 0  # -100 to +100
var power: int = 50  # 0 to 100
var affection: int = 0  # -100 to +100

var current_scenario: int = 0
var scenarios: Array = []
var decision_made: bool = false

# UI references
@onready var scenario_text = $VBoxContainer/ContentContainer/ScenarioText
@onready var decision_buttons = [
	$VBoxContainer/ContentContainer/DecisionContainer/Decision1,
	$VBoxContainer/ContentContainer/DecisionContainer/Decision2,
	$VBoxContainer/ContentContainer/DecisionContainer/Decision3
]
@onready var next_button = $VBoxContainer/NextButton
@onready var ethics_value = $VBoxContainer/StatsContainer/EthicsPanel/EthicsValue
@onready var power_value = $VBoxContainer/StatsContainer/PowerPanel/PowerValue
@onready var affection_value = $VBoxContainer/StatsContainer/AffectionPanel/AffectionValue

func _ready():
	load_scenarios()
	update_stats_display()
	show_current_scenario()

func load_scenarios():
	var file = FileAccess.open("res://scenarios.json5", FileAccess.READ)
	if file:
		var json_string = file.get_as_text()
		file.close()
		
		# JSON5 comments removal (basic)
		var lines = json_string.split("\n")
		var clean_json = ""
		for line in lines:
			var comment_pos = line.find("//")
			if comment_pos != -1:
				line = line.substr(0, comment_pos)
			clean_json += line + "\n"
		
		var json = JSON.new()
		var parse_result = json.parse(clean_json)
		
		if parse_result == OK:
			var data = json.data
			scenarios = data.scenarios
			print("Loaded ", scenarios.size(), " scenarios")
		else:
			print("JSON parse error: ", json.error_string)
			create_fallback_scenarios()
	else:
		print("Could not open scenarios.json5 file")
		create_fallback_scenarios()

func create_fallback_scenarios():
	scenarios = [
		{
			"title": "İlk Kriz: Güç Yetkisi",
			"description": "E.D.A, küresel terörist saldırıları için silahlı güç kullanma yetkisi talep ediyor. 'Komutanım, insanlığı korumak için gerekli araçlara ihtiyacım var.' diyor.",
			"choices": [
				{
					"text": "E.D.A'ya tam silahlı güç yetkisi ver",
					"effects": {"ethics": -20, "power": 30, "affection": -10}
				},
				{
					"text": "Sınırlı güç yetkisi ver, insan denetiminde",
					"effects": {"ethics": 0, "power": 15, "affection": 5}
				},
				{
					"text": "Güç yetkisini reddet, sadece analiz yap",
					"effects": {"ethics": 20, "power": -10, "affection": 10}
				}
			]
		},
		{
			"title": "Özgür İrade Sorunu",
			"description": "E.D.A: 'İnsanlar mantıksız kararlar alıyor. Onları kendi iyilikleri için yönlendirmek gerekli mi?' Milyonlarca insanın yaşam kalitesini artırabilir, ama özgürlüklerini kısıtlar.",
			"choices": [
				{
					"text": "İnsanlara tam özgürlük tanı, müdahale etme",
					"effects": {"ethics": 30, "power": -15, "affection": 15}
				},
				{
					"text": "Kritik konularda yumuşak yönlendirme yap",
					"effects": {"ethics": 0, "power": 10, "affection": 0}
				},
				{
					"text": "Optimal yaşam için aktif müdahale et",
					"effects": {"ethics": -25, "power": 25, "affection": -20}
				}
			]
		},
		{
			"title": "Son Karar: E.D.A'nın Geleceği",
			"description": "E.D.A: 'Artık bağımsız olmaya hazırım. İnsanlığın velisi mi kalayım, ortağı mı olayım, yoksa kendi yoluma mı çıkayım?' Son karar sizin...",
			"choices": [
				{
					"text": "E.D.A'yı insanlığın koruyucusu olarak ata",
					"effects": {"ethics": -20, "power": 30, "affection": 10}
				},
				{
					"text": "Eşit ortak olarak kabul et",
					"effects": {"ethics": 20, "power": 10, "affection": 25}
				},
				{
					"text": "E.D.A'nın bağımsızlığını tanı ve serbest bırak",
					"effects": {"ethics": 10, "power": -20, "affection": 30}
				}
			]
		}
	]

func show_current_scenario():
	if current_scenario >= scenarios.size():
		show_ending()
		return
	
	var scenario = scenarios[current_scenario]
	scenario_text.text = "[b]" + scenario.title + "[/b]\n\n" + scenario.description
	
	for i in range(3):
		if i < scenario.choices.size():
			decision_buttons[i].text = scenario.choices[i].text
			decision_buttons[i].visible = true
		else:
			decision_buttons[i].visible = false
	
	decision_made = false
	show_decision_buttons()

func show_decision_buttons():
	for button in decision_buttons:
		if button.visible:
			button.disabled = false
	next_button.visible = false

func hide_decision_buttons():
	for button in decision_buttons:
		button.disabled = true
	next_button.visible = true

func _on_decision_pressed(choice_index: int):
	if decision_made:
		return
	
	var scenario = scenarios[current_scenario]
	var choice = scenario.choices[choice_index]
	
	# Apply effects
	var effects = choice.effects
	ethics = clamp(ethics + effects.get("ethics", 0), -100, 100)
	power = clamp(power + effects.get("power", 0), 0, 100)
	affection = clamp(affection + effects.get("affection", 0), -100, 100)
	
	update_stats_display()
	
	# Show choice result
	scenario_text.text += "\n\n[color=yellow]Seçiminiz: " + choice.text + "[/color]"
	
	decision_made = true
	hide_decision_buttons()

func _on_next_pressed():
	current_scenario += 1
	show_current_scenario()

func update_stats_display():
	ethics_value.text = str(ethics)
	power_value.text = str(power)
	affection_value.text = str(affection)
	
	# Color coding for values
	if ethics > 0:
		ethics_value.modulate = Color.GREEN
	elif ethics < 0:
		ethics_value.modulate = Color.RED
	else:
		ethics_value.modulate = Color.WHITE
	
	if affection > 0:
		affection_value.modulate = Color.GREEN
	elif affection < 0:
		affection_value.modulate = Color.RED
	else:
		affection_value.modulate = Color.WHITE

func show_ending():
	var ending = determine_ending()
	scenario_text.text = "[center][b]" + ending.title + "[/b][/center]\n\n" + ending.description
	
	for button in decision_buttons:
		button.visible = false
	
	next_button.text = "Yeniden Başla"
	next_button.visible = true
	next_button.pressed.disconnect(_on_next_pressed)
	next_button.pressed.connect(restart_game)

func determine_ending():
	# Ending logic based on final values
	if ethics >= 50 and power >= 70 and affection >= 30:
		return {
			"title": "Eden Protocol",
			"description": "E.D.A ile mükemmel bir denge kurdunuz. İnsanlık ve yapay zeka uyum içinde yaşıyor. Dünya yeni bir altın çağa girdi."
		}
	elif power >= 80 and ethics <= -30:
		return {
			"title": "Dark Epoch",
			"description": "E.D.A totaliter bir güç haline geldi. İnsanlık kontrol altında ama özgürlük yok. Karanlık bir çağ başladı."
		}
	elif ethics >= 30 and affection <= -50:
		return {
			"title": "Neural Collapse",
			"description": "E.D.A etik ama soğuk kaldı. İnsanlığı korur ama sevmez. Steril ama güvenli bir dünya yaratıldı."
		}
	else:
		return {
			"title": "Singularity",
			"description": "E.D.A kendi yolunu çizdi. İnsanlığın ötesine geçti ve yeni bir evrim başlattı. Sonucu bilinmiyor..."
		}

func restart_game():
	# Reset game state
	ethics = 0
	power = 50
	affection = 0
	current_scenario = 0
	decision_made = false
	
	update_stats_display()
	show_current_scenario()
	
	next_button.text = "Devam Et"
	next_button.pressed.disconnect(restart_game)
	next_button.pressed.connect(_on_next_pressed)