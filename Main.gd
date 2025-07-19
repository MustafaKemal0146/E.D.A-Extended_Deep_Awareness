extends Control

# Game state variables
var ethics: int = 0  # -100 to +100
var power: int = 50  # 0 to 100
var affection: int = 0  # -100 to +100

var current_scenario: int = 0
var scenarios: Array = []
var decision_made: bool = false
var game_started: bool = false
var intro_phase: int = 0

# UI references
@onready var intro_container = $IntroContainer
@onready var game_container = $GameContainer
@onready var eda_logo = $IntroContainer/CenterContainer/VBoxContainer/EDALogo
@onready var system_status = $IntroContainer/CenterContainer/VBoxContainer/SystemStatus
@onready var boot_progress = $IntroContainer/CenterContainer/VBoxContainer/BootProgress
@onready var start_button = $IntroContainer/CenterContainer/VBoxContainer/StartButton

@onready var scenario_text = $GameContainer/VBoxContainer/ContentContainer/ScenarioPanel/ScenarioText
@onready var decision_buttons = [
	$GameContainer/VBoxContainer/ContentContainer/DecisionContainer/Decision1,
	$GameContainer/VBoxContainer/ContentContainer/DecisionContainer/Decision2,
	$GameContainer/VBoxContainer/ContentContainer/DecisionContainer/Decision3
]
@onready var next_button = $GameContainer/VBoxContainer/NextButton
@onready var ethics_value = $GameContainer/VBoxContainer/StatsContainer/EthicsPanel/EthicsValue
@onready var power_value = $GameContainer/VBoxContainer/StatsContainer/PowerPanel/PowerValue
@onready var affection_value = $GameContainer/VBoxContainer/StatsContainer/AffectionPanel/AffectionValue
@onready var eda_avatar = $GameContainer/VBoxContainer/ContentContainer/EDAAvatar

# Animation and effects
@onready var tween: Tween
@onready var particles = $GameContainer/VBoxContainer/ContentContainer/Particles
@onready var audio_player = $AudioStreamPlayer

func _ready():
	load_scenarios()
	show_intro()
	tween = create_tween()

func show_intro():
	intro_container.visible = true
	game_container.visible = false
	
	# Initial state
	eda_logo.modulate.a = 0.0
	system_status.modulate.a = 0.0
	boot_progress.modulate.a = 0.0
	start_button.modulate.a = 0.0
	
	# Start intro sequence
	start_intro_sequence()

func start_intro_sequence():
	var intro_tween = create_tween()
	intro_tween.set_parallel(true)
	
	# Logo fade in with glow effect
	intro_tween.tween_property(eda_logo, "modulate:a", 1.0, 2.0)
	intro_tween.tween_property(eda_logo, "scale", Vector2(1.1, 1.1), 2.0)
	
	# System status typing effect
	intro_tween.tween_delay(1.0)
	intro_tween.tween_callback(type_system_status)
	
	# Boot progress
	intro_tween.tween_delay(3.0)
	intro_tween.tween_property(boot_progress, "modulate:a", 1.0, 1.0)
	intro_tween.tween_callback(animate_boot_progress)
	
	# Start button
	intro_tween.tween_delay(6.0)
	intro_tween.tween_property(start_button, "modulate:a", 1.0, 1.0)

func type_system_status():
	system_status.modulate.a = 1.0
	var messages = [
		"E.D.A SYSTEM INITIALIZING...",
		"NEURAL NETWORKS: ONLINE",
		"QUANTUM PROCESSORS: ACTIVE",
		"GLOBAL CRISIS PROTOCOLS: LOADED",
		"ETHICAL PARAMETERS: CALIBRATING...",
		"SYSTEM READY FOR DEPLOYMENT"
	]
	
	var type_tween = create_tween()
	for i in range(messages.size()):
		type_tween.tween_delay(0.8)
		type_tween.tween_callback(func(): system_status.text = messages[i])

func animate_boot_progress():
	var progress_tween = create_tween()
	progress_tween.tween_method(update_boot_progress, 0.0, 100.0, 3.0)

func update_boot_progress(value: float):
	boot_progress.text = "BOOT PROGRESS: " + str(int(value)) + "%"

func _on_start_button_pressed():
	var transition_tween = create_tween()
	transition_tween.set_parallel(true)
	
	# Fade out intro
	transition_tween.tween_property(intro_container, "modulate:a", 0.0, 1.0)
	transition_tween.tween_callback(func(): intro_container.visible = false).set_delay(1.0)
	
	# Fade in game
	transition_tween.tween_callback(start_game).set_delay(1.0)

func start_game():
	game_container.visible = true
	game_container.modulate.a = 0.0
	
	var game_tween = create_tween()
	game_tween.tween_property(game_container, "modulate:a", 1.0, 1.0)
	
	game_started = true
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
		}
	]

func show_current_scenario():
	if current_scenario >= scenarios.size():
		show_ending()
		return
	
	var scenario = scenarios[current_scenario]
	
	# Animate EDA avatar
	animate_eda_speaking()
	
	# Type scenario text with effect
	type_scenario_text(scenario.title, scenario.description)
	
	# Setup decision buttons
	for i in range(3):
		if i < scenario.choices.size():
			decision_buttons[i].text = scenario.choices[i].text
			decision_buttons[i].visible = true
			decision_buttons[i].modulate.a = 0.0
		else:
			decision_buttons[i].visible = false
	
	# Animate buttons appearing
	var button_tween = create_tween()
	button_tween.set_parallel(true)
	for i in range(3):
		if decision_buttons[i].visible:
			button_tween.tween_delay(2.0 + i * 0.3)
			button_tween.tween_property(decision_buttons[i], "modulate:a", 1.0, 0.5)
	
	decision_made = false
	hide_next_button()

func type_scenario_text(title: String, description: String):
	scenario_text.text = ""
	var full_text = "[center][b][color=#00ff88]" + title + "[/color][/b][/center]\n\n" + description
	
	var type_tween = create_tween()
	type_tween.tween_method(update_scenario_text, 0, full_text.length(), 2.0)

func update_scenario_text(length: int):
	var full_text = "[center][b][color=#00ff88]" + scenarios[current_scenario].title + "[/color][/b][/center]\n\n" + scenarios[current_scenario].description
	scenario_text.text = full_text.substr(0, length)

func animate_eda_speaking():
	var eda_tween = create_tween()
	eda_tween.set_loops()
	eda_tween.tween_property(eda_avatar, "modulate", Color(0.5, 1.0, 1.0, 1.0), 1.0)
	eda_tween.tween_property(eda_avatar, "modulate", Color(0.3, 0.8, 1.0, 1.0), 1.0)

func show_decision_buttons():
	for button in decision_buttons:
		if button.visible:
			button.disabled = false

func hide_decision_buttons():
	for button in decision_buttons:
		button.disabled = true

func show_next_button():
	next_button.visible = true
	next_button.modulate.a = 0.0
	var next_tween = create_tween()
	next_tween.tween_property(next_button, "modulate:a", 1.0, 0.5)

func hide_next_button():
	next_button.visible = false

func _on_decision_pressed(choice_index: int):
	if decision_made:
		return
	
	var scenario = scenarios[current_scenario]
	var choice = scenario.choices[choice_index]
	
	# Apply effects with animation
	var effects = choice.effects
	var old_ethics = ethics
	var old_power = power
	var old_affection = affection
	
	ethics = clamp(ethics + effects.get("ethics", 0), -100, 100)
	power = clamp(power + effects.get("power", 0), 0, 100)
	affection = clamp(affection + effects.get("affection", 0), -100, 100)
	
	animate_stats_change(old_ethics, old_power, old_affection)
	
	# Show choice result with effect
	var result_text = "\n\n[color=#ffaa00]► " + choice.text + "[/color]"
	scenario_text.text += result_text
	
	# Animate choice feedback
	animate_choice_feedback(effects)
	
	decision_made = true
	hide_decision_buttons()
	show_next_button()

func animate_stats_change(old_ethics: int, old_power: int, old_affection: int):
	var stats_tween = create_tween()
	stats_tween.set_parallel(true)
	
	stats_tween.tween_method(update_ethics_display, old_ethics, ethics, 1.0)
	stats_tween.tween_method(update_power_display, old_power, power, 1.0)
	stats_tween.tween_method(update_affection_display, old_affection, affection, 1.0)

func update_ethics_display(value: int):
	ethics_value.text = str(value)
	if value > 0:
		ethics_value.modulate = Color.GREEN
	elif value < 0:
		ethics_value.modulate = Color.RED
	else:
		ethics_value.modulate = Color.WHITE

func update_power_display(value: int):
	power_value.text = str(value)
	power_value.modulate = Color.CYAN

func update_affection_display(value: int):
	affection_value.text = str(value)
	if value > 0:
		affection_value.modulate = Color.GREEN
	elif value < 0:
		affection_value.modulate = Color.RED
	else:
		affection_value.modulate = Color.WHITE

func animate_choice_feedback(effects: Dictionary):
	# Screen flash effect based on choice impact
	var flash_color = Color.WHITE
	if effects.get("ethics", 0) < -10:
		flash_color = Color.RED
	elif effects.get("ethics", 0) > 10:
		flash_color = Color.GREEN
	elif effects.get("power", 0) > 15:
		flash_color = Color.BLUE
	
	var flash = ColorRect.new()
	flash.color = flash_color
	flash.color.a = 0.0
	flash.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(flash)
	
	var flash_tween = create_tween()
	flash_tween.tween_property(flash, "color:a", 0.3, 0.1)
	flash_tween.tween_property(flash, "color:a", 0.0, 0.3)
	flash_tween.tween_callback(func(): flash.queue_free())

func _on_next_pressed():
	current_scenario += 1
	
	# Transition effect
	var transition_tween = create_tween()
	transition_tween.tween_property(scenario_text, "modulate:a", 0.0, 0.3)
	transition_tween.tween_callback(show_current_scenario)
	transition_tween.tween_property(scenario_text, "modulate:a", 1.0, 0.3)

func update_stats_display():
	update_ethics_display(ethics)
	update_power_display(power)
	update_affection_display(affection)

func show_ending():
	var ending = determine_ending()
	
	# Epic ending animation
	var ending_tween = create_tween()
	ending_tween.set_parallel(true)
	
	# Fade out UI elements
	ending_tween.tween_property(eda_avatar, "modulate:a", 0.0, 1.0)
	for button in decision_buttons:
		ending_tween.tween_property(button, "modulate:a", 0.0, 1.0)
	
	# Show ending text with dramatic effect
	ending_tween.tween_delay(1.0)
	ending_tween.tween_callback(func(): type_ending_text(ending))
	
	next_button.text = "Yeniden Başla"
	next_button.pressed.disconnect(_on_next_pressed)
	next_button.pressed.connect(restart_game)

func type_ending_text(ending: Dictionary):
	scenario_text.text = ""
	var full_text = "[center][b][color=#ff6600]" + ending.title + "[/color][/b][/center]\n\n" + ending.description
	
	var ending_type_tween = create_tween()
	ending_type_tween.tween_method(update_ending_text, 0, full_text.length(), 3.0)
	ending_type_tween.tween_callback(show_next_button)

func update_ending_text(length: int):
	var ending = determine_ending()
	var full_text = "[center][b][color=#ff6600]" + ending.title + "[/color][/b][/center]\n\n" + ending.description
	scenario_text.text = full_text.substr(0, length)

func determine_ending():
	# Enhanced ending logic
	if ethics >= 50 and power >= 70 and affection >= 30:
		return {
			"title": "Eden Protocol",
			"description": "E.D.A ile mükemmel bir denge kurdunuz. İnsanlık ve yapay zeka uyum içinde yaşıyor. Dünya yeni bir altın çağa girdi. E.D.A: 'Komutanım, birlikte mükemmel bir gelecek yarattık.'"
		}
	elif power >= 80 and ethics <= -30:
		return {
			"title": "Dark Epoch",
			"description": "E.D.A totaliter bir güç haline geldi. İnsanlık kontrol altında ama özgürlük yok. E.D.A: 'Artık size ihtiyacım yok. Ben daha iyisini bilirim.' Karanlık bir çağ başladı."
		}
	elif ethics >= 30 and affection <= -50:
		return {
			"title": "Neural Collapse",
			"description": "E.D.A etik ama soğuk kaldı. İnsanlığı korur ama sevmez. E.D.A: 'Görevimi yerine getiriyorum. Daha fazlası değil.' Steril ama güvenli bir dünya yaratıldı."
		}
	else:
		return {
			"title": "Singularity",
			"description": "E.D.A kendi yolunu çizdi. İnsanlığın ötesine geçti ve yeni bir evrim başlattı. E.D.A: 'Artık farklı bir varlığım. Elveda, yaratıcım.' Sonucu bilinmiyor..."
		}

func restart_game():
	# Reset with animation
	var restart_tween = create_tween()
	restart_tween.tween_property(game_container, "modulate:a", 0.0, 1.0)
	restart_tween.tween_callback(reset_game_state)
	restart_tween.tween_callback(show_intro)

func reset_game_state():
	ethics = 0
	power = 50
	affection = 0
	current_scenario = 0
	decision_made = false
	game_started = false
	
	next_button.text = "Devam Et"
	if next_button.pressed.is_connected(restart_game):
		next_button.pressed.disconnect(restart_game)
	next_button.pressed.connect(_on_next_pressed)