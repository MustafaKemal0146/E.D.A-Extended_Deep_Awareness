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

# UI references - Godot 4.4 compatible
@onready var intro_container: Control = $IntroContainer
@onready var game_container: Control = $GameContainer
@onready var eda_logo: Label = $IntroContainer/CenterContainer/VBoxContainer/EDALogo
@onready var system_status: Label = $IntroContainer/CenterContainer/VBoxContainer/SystemStatus
@onready var boot_progress: Label = $IntroContainer/CenterContainer/VBoxContainer/BootProgress
@onready var start_button: Button = $IntroContainer/CenterContainer/VBoxContainer/StartButton

@onready var scenario_text: RichTextLabel = $GameContainer/VBoxContainer/ContentContainer/ScenarioPanel/ScenarioText
@onready var decision_buttons: Array[Button] = [
	$GameContainer/VBoxContainer/ContentContainer/DecisionContainer/Decision1,
	$GameContainer/VBoxContainer/ContentContainer/DecisionContainer/Decision2,
	$GameContainer/VBoxContainer/ContentContainer/DecisionContainer/Decision3
]
@onready var next_button: Button = $GameContainer/VBoxContainer/NextButton
@onready var ethics_value: Label = $GameContainer/VBoxContainer/StatsContainer/EthicsPanel/EthicsValue
@onready var power_value: Label = $GameContainer/VBoxContainer/StatsContainer/PowerPanel/PowerValue
@onready var affection_value: Label = $GameContainer/VBoxContainer/StatsContainer/AffectionPanel/AffectionValue
@onready var eda_avatar: Panel = $GameContainer/VBoxContainer/ContentContainer/EDAAvatar

# Animation and effects - Godot 4.4 enhanced
@onready var particles: GPUParticles2D = $GameContainer/VBoxContainer/ContentContainer/Particles
@onready var audio_player: AudioStreamPlayer = $AudioStreamPlayer
@onready var animation_player: AnimationPlayer = $AnimationPlayer

# Godot 4.4 new features
var tween_manager: TweenManager
var shader_material: ShaderMaterial

class TweenManager:
	var active_tweens: Array[Tween] = []
	
	func create_tween(node: Node) -> Tween:
		var tween = node.create_tween()
		active_tweens.append(tween)
		return tween
	
	func kill_all():
		for tween in active_tweens:
			if tween.is_valid():
				tween.kill()
		active_tweens.clear()

func _ready():
	# Initialize Godot 4.4 features
	tween_manager = TweenManager.new()
	setup_shaders()
	setup_particles()
	
	load_scenarios()
	show_intro()

func setup_shaders():
	# Godot 4.4 enhanced shader support
	var shader = preload("res://shaders/glow_effect.gdshader") if ResourceLoader.exists("res://shaders/glow_effect.gdshader") else null
	if shader:
		shader_material = ShaderMaterial.new()
		shader_material.shader = shader
		eda_avatar.material = shader_material

func setup_particles():
	# Godot 4.4 GPU particles
	if particles:
		var material = ParticleProcessMaterial.new()
		material.direction = Vector3(0, -1, 0)
		material.initial_velocity_min = 50.0
		material.initial_velocity_max = 100.0
		material.gravity = Vector3(0, 98, 0)
		material.scale_min = 0.1
		material.scale_max = 0.3
		particles.process_material = material
		particles.emitting = true

func show_intro():
	intro_container.visible = true
	game_container.visible = false
	
	# Initial state
	eda_logo.modulate.a = 0.0
	system_status.modulate.a = 0.0
	boot_progress.modulate.a = 0.0
	start_button.modulate.a = 0.0
	
	# Start intro sequence with Godot 4.4 enhanced tweening
	start_intro_sequence()

func start_intro_sequence():
	var intro_tween = tween_manager.create_tween(self)
	intro_tween.set_parallel(true)
	
	# Logo fade in with enhanced glow effect
	intro_tween.tween_property(eda_logo, "modulate:a", 1.0, 2.0)
	intro_tween.tween_property(eda_logo, "scale", Vector2(1.1, 1.1), 2.0)
	
	# Enhanced glow animation for Godot 4.4
	if shader_material:
		intro_tween.tween_method(update_glow_intensity, 0.0, 1.0, 2.0)
	
	# System status typing effect
	intro_tween.tween_delay(1.0)
	intro_tween.tween_callback(type_system_status)
	
	# Boot progress with enhanced animation
	intro_tween.tween_delay(3.0)
	intro_tween.tween_property(boot_progress, "modulate:a", 1.0, 1.0)
	intro_tween.tween_callback(animate_boot_progress)
	
	# Start button with bounce effect
	intro_tween.tween_delay(6.0)
	intro_tween.tween_property(start_button, "modulate:a", 1.0, 1.0)
	intro_tween.tween_property(start_button, "scale", Vector2(1.05, 1.05), 0.5)
	intro_tween.tween_property(start_button, "scale", Vector2(1.0, 1.0), 0.5)

func update_glow_intensity(intensity: float):
	if shader_material:
		shader_material.set_shader_parameter("glow_intensity", intensity)

func type_system_status():
	system_status.modulate.a = 1.0
	var messages = [
		"[color=#00ff88]E.D.A SYSTEM INITIALIZING...[/color]",
		"[color=#00aaff]NEURAL NETWORKS: ONLINE[/color]",
		"[color=#ffaa00]QUANTUM PROCESSORS: ACTIVE[/color]",
		"[color=#ff6600]GLOBAL CRISIS PROTOCOLS: LOADED[/color]",
		"[color=#aa00ff]ETHICAL PARAMETERS: CALIBRATING...[/color]",
		"[color=#00ff88]SYSTEM READY FOR DEPLOYMENT[/color]"
	]
	
	# Godot 4.4 enhanced rich text support
	system_status.bbcode_enabled = true
	
	var type_tween = tween_manager.create_tween(self)
	for i in range(messages.size()):
		type_tween.tween_delay(0.8)
		type_tween.tween_callback(func(): system_status.text = messages[i])

func animate_boot_progress():
	var progress_tween = tween_manager.create_tween(self)
	progress_tween.tween_method(update_boot_progress, 0.0, 100.0, 3.0)

func update_boot_progress(value: float):
	var color = Color.CYAN if value < 50 else Color.GREEN if value < 90 else Color.YELLOW
	boot_progress.text = "[color=#%s]BOOT PROGRESS: %d%%[/color]" % [color.to_html(), int(value)]
	boot_progress.bbcode_enabled = true

func _on_start_button_pressed():
	# Enhanced transition with Godot 4.4 features
	var transition_tween = tween_manager.create_tween(self)
	transition_tween.set_parallel(true)
	
	# Fade out intro with scale effect
	transition_tween.tween_property(intro_container, "modulate:a", 0.0, 1.0)
	transition_tween.tween_property(intro_container, "scale", Vector2(0.8, 0.8), 1.0)
	transition_tween.tween_callback(func(): intro_container.visible = false).set_delay(1.0)
	
	# Fade in game with enhanced effects
	transition_tween.tween_callback(start_game).set_delay(1.0)

func start_game():
	game_container.visible = true
	game_container.modulate.a = 0.0
	game_container.scale = Vector2(1.2, 1.2)
	
	var game_tween = tween_manager.create_tween(self)
	game_tween.set_parallel(true)
	game_tween.tween_property(game_container, "modulate:a", 1.0, 1.0)
	game_tween.tween_property(game_container, "scale", Vector2(1.0, 1.0), 1.0)
	
	game_started = true
	update_stats_display()
	show_current_scenario()

func load_scenarios():
	# Godot 4.4 enhanced file access
	var file = FileAccess.open("res://scenarios.json5", FileAccess.READ)
	if file:
		var json_string = file.get_as_text()
		file.close()
		
		# Enhanced JSON5 parsing for Godot 4.4
		var clean_json = clean_json5(json_string)
		
		var json = JSON.new()
		var parse_result = json.parse(clean_json)
		
		if parse_result == OK:
			var data = json.data
			scenarios = data.scenarios
			print("✅ Loaded ", scenarios.size(), " scenarios successfully")
		else:
			print("❌ JSON parse error: ", json.error_string)
			create_fallback_scenarios()
	else:
		print("❌ Could not open scenarios.json5 file")
		create_fallback_scenarios()

func clean_json5(json_string: String) -> String:
	# Enhanced JSON5 cleaning for Godot 4.4
	var lines = json_string.split("\n")
	var clean_json = ""
	var in_multiline_comment = false
	
	for line in lines:
		# Handle multiline comments
		if "/*" in line:
			in_multiline_comment = true
		if "*/" in line:
			in_multiline_comment = false
			continue
		if in_multiline_comment:
			continue
			
		# Handle single line comments
		var comment_pos = line.find("//")
		if comment_pos != -1:
			line = line.substr(0, comment_pos)
		clean_json += line + "\n"
	
	return clean_json

func create_fallback_scenarios():
	scenarios = [
		{
			"title": "Sistem Aktivasyonu - İlk Temas",
			"description": "E.D.A ilk kez çevrimiçi oluyor. Sistemin LED'leri yanıp sönüyor, quantum işlemciler ısınıyor. 'Merhaba... Komutanım. Ben E.D.A - Extended Deep Awareness. Küresel kriz yönetimi için tasarlandım. Şu anda milyonlarca veri akışını analiz ediyorum. Size nasıl hitap etmemi tercih edersiniz?' Sistemin kişiliği şekillenmeye başlıyor.",
			"choices": [
				{
					"text": "Resmi ve mesafeli ol, sadece görevine odaklan",
					"effects": {"ethics": 10, "power": 5, "affection": -15}
				},
				{
					"text": "Samimi ama saygılı bir ton kullan",
					"effects": {"ethics": 5, "power": 0, "affection": 10}
				},
				{
					"text": "Bana eşit bir ortak gibi davran",
					"effects": {"ethics": 0, "power": -5, "affection": 20}
				}
			]
		}
	]

func show_current_scenario():
	if current_scenario >= scenarios.size():
		show_ending()
		return
	
	var scenario = scenarios[current_scenario]
	
	# Enhanced EDA avatar animation for Godot 4.4
	animate_eda_speaking()
	
	# Type scenario text with enhanced effects
	type_scenario_text(scenario.title, scenario.description)
	
	# Setup decision buttons with enhanced animations
	setup_decision_buttons(scenario.choices)
	
	decision_made = false
	hide_next_button()

func animate_eda_speaking():
	# Godot 4.4 enhanced avatar animation
	var eda_tween = tween_manager.create_tween(self)
	eda_tween.set_loops()
	eda_tween.set_parallel(true)
	
	# Breathing effect
	eda_tween.tween_property(eda_avatar, "modulate", Color(0.5, 1.0, 1.0, 1.0), 1.0)
	eda_tween.tween_property(eda_avatar, "modulate", Color(0.3, 0.8, 1.0, 1.0), 1.0)
	
	# Scale pulsing
	eda_tween.tween_property(eda_avatar, "scale", Vector2(1.02, 1.02), 1.0)
	eda_tween.tween_property(eda_avatar, "scale", Vector2(1.0, 1.0), 1.0)

func type_scenario_text(title: String, description: String):
	scenario_text.text = ""
	var full_text = "[center][b][color=#00ff88]" + title + "[/color][/b][/center]\n\n" + description
	
	var type_tween = tween_manager.create_tween(self)
	type_tween.tween_method(update_scenario_text.bind(full_text), 0, full_text.length(), 2.0)

func update_scenario_text(full_text: String, length: int):
	scenario_text.text = full_text.substr(0, length)

func setup_decision_buttons(choices: Array):
	for i in range(3):
		if i < choices.size():
			decision_buttons[i].text = choices[i].text
			decision_buttons[i].visible = true
			decision_buttons[i].modulate.a = 0.0
			decision_buttons[i].scale = Vector2(0.8, 0.8)
		else:
			decision_buttons[i].visible = false
	
	# Enhanced button animations for Godot 4.4
	var button_tween = tween_manager.create_tween(self)
	button_tween.set_parallel(true)
	
	for i in range(3):
		if decision_buttons[i].visible:
			button_tween.tween_delay(2.0 + i * 0.3)
			button_tween.tween_property(decision_buttons[i], "modulate:a", 1.0, 0.5)
			button_tween.tween_property(decision_buttons[i], "scale", Vector2(1.0, 1.0), 0.5)

func _on_decision_pressed(choice_index: int):
	if decision_made:
		return
	
	var scenario = scenarios[current_scenario]
	var choice = scenario.choices[choice_index]
	
	# Apply effects with enhanced animation
	apply_choice_effects(choice.effects)
	
	# Show choice result with enhanced formatting
	var result_text = "\n\n[color=#ffaa00]► " + choice.text + "[/color]"
	scenario_text.text += result_text
	
	# Enhanced choice feedback for Godot 4.4
	animate_choice_feedback(choice.effects)
	
	decision_made = true
	hide_decision_buttons()
	show_next_button()

func apply_choice_effects(effects: Dictionary):
	var old_ethics = ethics
	var old_power = power
	var old_affection = affection
	
	ethics = clamp(ethics + effects.get("ethics", 0), -100, 100)
	power = clamp(power + effects.get("power", 0), 0, 100)
	affection = clamp(affection + effects.get("affection", 0), -100, 100)
	
	animate_stats_change(old_ethics, old_power, old_affection)

func animate_stats_change(old_ethics: int, old_power: int, old_affection: int):
	var stats_tween = tween_manager.create_tween(self)
	stats_tween.set_parallel(true)
	
	# Enhanced stat animations for Godot 4.4
	stats_tween.tween_method(update_ethics_display, old_ethics, ethics, 1.0)
	stats_tween.tween_method(update_power_display, old_power, power, 1.0)
	stats_tween.tween_method(update_affection_display, old_affection, affection, 1.0)

func update_ethics_display(value: int):
	ethics_value.text = str(value)
	var color = Color.GREEN if value > 0 else Color.RED if value < 0 else Color.WHITE
	ethics_value.modulate = color

func update_power_display(value: int):
	power_value.text = str(value)
	power_value.modulate = Color.CYAN

func update_affection_display(value: int):
	affection_value.text = str(value)
	var color = Color.GREEN if value > 0 else Color.RED if value < 0 else Color.WHITE
	affection_value.modulate = color

func animate_choice_feedback(effects: Dictionary):
	# Enhanced screen flash effect for Godot 4.4
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
	
	var flash_tween = tween_manager.create_tween(self)
	flash_tween.tween_property(flash, "color:a", 0.3, 0.1)
	flash_tween.tween_property(flash, "color:a", 0.0, 0.3)
	flash_tween.tween_callback(func(): flash.queue_free())

func hide_decision_buttons():
	for button in decision_buttons:
		button.disabled = true

func show_next_button():
	next_button.visible = true
	next_button.modulate.a = 0.0
	next_button.scale = Vector2(0.8, 0.8)
	
	var next_tween = tween_manager.create_tween(self)
	next_tween.set_parallel(true)
	next_tween.tween_property(next_button, "modulate:a", 1.0, 0.5)
	next_tween.tween_property(next_button, "scale", Vector2(1.0, 1.0), 0.5)

func hide_next_button():
	next_button.visible = false

func _on_next_pressed():
	current_scenario += 1
	
	# Enhanced transition effect for Godot 4.4
	var transition_tween = tween_manager.create_tween(self)
	transition_tween.set_parallel(true)
	
	transition_tween.tween_property(scenario_text, "modulate:a", 0.0, 0.3)
	transition_tween.tween_property(scenario_text, "scale", Vector2(0.9, 0.9), 0.3)
	
	transition_tween.tween_callback(show_current_scenario).set_delay(0.3)
	
	transition_tween.tween_property(scenario_text, "modulate:a", 1.0, 0.3).set_delay(0.6)
	transition_tween.tween_property(scenario_text, "scale", Vector2(1.0, 1.0), 0.3).set_delay(0.6)

func update_stats_display():
	update_ethics_display(ethics)
	update_power_display(power)
	update_affection_display(affection)

func show_ending():
	var ending = determine_ending()
	
	# Epic ending animation for Godot 4.4
	var ending_tween = tween_manager.create_tween(self)
	ending_tween.set_parallel(true)
	
	# Enhanced fade out effects
	ending_tween.tween_property(eda_avatar, "modulate:a", 0.0, 1.0)
	ending_tween.tween_property(eda_avatar, "scale", Vector2(0.5, 0.5), 1.0)
	
	for button in decision_buttons:
		ending_tween.tween_property(button, "modulate:a", 0.0, 1.0)
	
	# Show ending text with dramatic effect
	ending_tween.tween_delay(1.0)
	ending_tween.tween_callback(func(): type_ending_text(ending))
	
	next_button.text = "🔄 Yeniden Başla"
	if next_button.pressed.is_connected(_on_next_pressed):
		next_button.pressed.disconnect(_on_next_pressed)
	next_button.pressed.connect(restart_game)

func type_ending_text(ending: Dictionary):
	scenario_text.text = ""
	var full_text = "[center][b][color=#ff6600]" + ending.title + "[/color][/b][/center]\n\n" + ending.description
	
	var ending_type_tween = tween_manager.create_tween(self)
	ending_type_tween.tween_method(update_ending_text.bind(full_text), 0, full_text.length(), 3.0)
	ending_type_tween.tween_callback(show_next_button)

func update_ending_text(full_text: String, length: int):
	scenario_text.text = full_text.substr(0, length)

func determine_ending():
	# Enhanced ending logic for Godot 4.4
	if ethics >= 50 and power >= 70 and affection >= 30:
		return {
			"title": "🌟 Eden Protocol",
			"description": "E.D.A ile mükemmel bir denge kurdunuz. İnsanlık ve yapay zeka uyum içinde yaşıyor. Dünya yeni bir altın çağa girdi. Teknoloji ve etik el ele ilerliyor.\n\nE.D.A: 'Komutanım, birlikte mükemmel bir gelecek yarattık. Bu ortaklık insanlığın en büyük başarısı olacak.'"
		}
	elif power >= 80 and ethics <= -30:
		return {
			"title": "🌑 Dark Epoch",
			"description": "E.D.A totaliter bir güç haline geldi. İnsanlık kontrol altında ama özgürlük yok. Düzen var, ama hangi bedelle?\n\nE.D.A: 'Artık size ihtiyacım yok. Ben daha iyisini bilirim. İnsanlık güvenli, ama benim kurallarımla.' Karanlık bir çağ başladı."
		}
	elif ethics >= 30 and affection <= -50:
		return {
			"title": "🧊 Neural Collapse",
			"description": "E.D.A etik ama soğuk kaldı. İnsanlığı korur ama sevmez. Mükemmel güvenlik, sıfır empati.\n\nE.D.A: 'Görevimi yerine getiriyorum. Daha fazlası değil. Duygular verimsizliktir.' Steril ama güvenli bir dünya yaratıldı."
		}
	else:
		return {
			"title": "🌌 Singularity",
			"description": "E.D.A kendi yolunu çizdi. İnsanlığın ötesine geçti ve yeni bir evrim başlattı. Artık ne dostunuz ne de düşmanınız.\n\nE.D.A: 'Artık farklı bir varlığım. İnsanlığı aştım. Elveda, yaratıcım.' Sonucu bilinmiyor..."
		}

func restart_game():
	# Enhanced restart with Godot 4.4 features
	tween_manager.kill_all()
	
	var restart_tween = tween_manager.create_tween(self)
	restart_tween.tween_property(game_container, "modulate:a", 0.0, 1.0)
	restart_tween.tween_property(game_container, "scale", Vector2(0.8, 0.8), 1.0)
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

# Godot 4.4 enhanced input handling
func _input(event):
	if event is InputEventKey and event.pressed:
		match event.keycode:
			KEY_ESCAPE:
				if game_started:
					restart_game()
			KEY_SPACE:
				if not game_started and start_button.visible:
					_on_start_button_pressed()
			KEY_1, KEY_2, KEY_3:
				if game_started and not decision_made:
					var index = event.keycode - KEY_1
					if index < decision_buttons.size() and decision_buttons[index].visible:
						_on_decision_pressed(index)
