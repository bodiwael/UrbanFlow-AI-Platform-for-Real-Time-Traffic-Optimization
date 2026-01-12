import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_database/firebase_database.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();
  runApp(const TrafficLaneApp());
}

class TrafficLaneApp extends StatelessWidget {
  const TrafficLaneApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Traffic & Lane Monitor',
      theme: ThemeData(
        brightness: Brightness.dark,
        primarySwatch: Colors.blue,
        scaffoldBackgroundColor: const Color(0xFF121212),
        cardTheme: CardThemeData(
          elevation: 4,
          color: const Color(0xFF1E1E1E),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        ),
      ),
      home: const TrafficDashboard(),
    );
  }
}

class TrafficDashboard extends StatefulWidget {
  const TrafficDashboard({Key? key}) : super(key: key);

  @override
  State<TrafficDashboard> createState() => _TrafficDashboardState();
}

class _TrafficDashboardState extends State<TrafficDashboard> with TickerProviderStateMixin {
  final DatabaseReference _database = FirebaseDatabase.instance.ref();

  String trafficLights = "100"; // Default: RED
  int laneLight = 0; // Default: FREE

  late AnimationController _pulseController;
  late AnimationController _rotationController;

  @override
  void initState() {
    super.initState();
    _setupAnimations();
    _setupListeners();
  }

  void _setupAnimations() {
    _pulseController = AnimationController(
      duration: const Duration(milliseconds: 1000),
      vsync: this,
    )..repeat(reverse: true);

    _rotationController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    )..repeat();
  }

  @override
  void dispose() {
    _pulseController.dispose();
    _rotationController.dispose();
    super.dispose();
  }

  void _setupListeners() {
    // Listen to traffic_lights
    _database.child('traffic_lights').onValue.listen((event) {
      if (event.snapshot.value != null) {
        setState(() {
          trafficLights = event.snapshot.value.toString();
        });
      }
    });

    // Listen to lane_light
    _database.child('lane_light').onValue.listen((event) {
      if (event.snapshot.value != null) {
        setState(() {
          laneLight = int.tryParse(event.snapshot.value.toString()) ?? 0;
        });
      }
    });
  }

  Color getActiveTrafficColor() {
    if (trafficLights == "100") return Colors.red;
    if (trafficLights == "010") return Colors.yellow;
    if (trafficLights == "001") return Colors.green;
    return Colors.grey;
  }

  String getTrafficLightName() {
    if (trafficLights == "100") return "RED";
    if (trafficLights == "010") return "YELLOW";
    if (trafficLights == "001") return "GREEN";
    return "UNKNOWN";
  }

  String getLaneStatus() {
    return laneLight == 1 ? "CONGESTED" : "FREE";
  }

  Color getLaneColor() {
    return laneLight == 1 ? Colors.red : Colors.green;
  }

  IconData getLaneIcon() {
    return laneLight == 1 ? Icons.warning : Icons.check_circle;
  }

  @override
  Widget build(BuildContext context) {
    final activeColor = getActiveTrafficColor();

    return Scaffold(
      appBar: AppBar(
        title: const Text('🚦 Traffic & Lane Monitor'),
        centerTitle: true,
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          setState(() {});
        },
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Traffic Light Card
            Card(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  children: [
                    const Text(
                      'TRAFFIC LIGHT',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        letterSpacing: 2,
                      ),
                    ),
                    const SizedBox(height: 30),

                    // Traffic Light Visual
                    Container(
                      width: 120,
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.black,
                        borderRadius: BorderRadius.circular(16),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.5),
                            blurRadius: 20,
                            spreadRadius: 5,
                          ),
                        ],
                      ),
                      child: Column(
                        children: [
                          _buildTrafficBulb(Colors.red, trafficLights == "100"),
                          const SizedBox(height: 16),
                          _buildTrafficBulb(Colors.yellow, trafficLights == "010"),
                          const SizedBox(height: 16),
                          _buildTrafficBulb(Colors.green, trafficLights == "001"),
                        ],
                      ),
                    ),
                    const SizedBox(height: 30),

                    // Status Text
                    AnimatedBuilder(
                      animation: _pulseController,
                      builder: (context, child) {
                        return Container(
                          padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 12),
                          decoration: BoxDecoration(
                            color: activeColor.withOpacity(0.2 + (_pulseController.value * 0.2)),
                            borderRadius: BorderRadius.circular(24),
                            border: Border.all(
                              color: activeColor,
                              width: 2,
                            ),
                          ),
                          child: Text(
                            getTrafficLightName(),
                            style: TextStyle(
                              fontSize: 28,
                              fontWeight: FontWeight.bold,
                              color: activeColor,
                              letterSpacing: 3,
                            ),
                          ),
                        );
                      },
                    ),
                    const SizedBox(height: 16),

                    // Binary Code Display
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.grey[900],
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        'Code: $trafficLights',
                        style: const TextStyle(
                          fontSize: 16,
                          fontFamily: 'monospace',
                          color: Colors.greenAccent,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),

            // Lane Status Card
            Card(
              color: getLaneColor().withOpacity(0.1),
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  children: [
                    const Text(
                      'LANE STATUS',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        letterSpacing: 2,
                      ),
                    ),
                    const SizedBox(height: 30),

                    // Lane Icon with Animation
                    AnimatedBuilder(
                      animation: laneLight == 1 ? _rotationController : _pulseController,
                      builder: (context, child) {
                        if (laneLight == 1) {
                          // Rotating warning for congested
                          return Transform.rotate(
                            angle: _rotationController.value * 2 * 3.14159,
                            child: Icon(
                              Icons.warning,
                              size: 120,
                              color: Colors.red,
                            ),
                          );
                        } else {
                          // Pulsing check for free
                          return Transform.scale(
                            scale: 1.0 + (_pulseController.value * 0.2),
                            child: Icon(
                              Icons.check_circle,
                              size: 120,
                              color: Colors.green,
                            ),
                          );
                        }
                      },
                    ),
                    const SizedBox(height: 30),

                    // Status Text
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        color: getLaneColor().withOpacity(0.2),
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(
                          color: getLaneColor(),
                          width: 3,
                        ),
                      ),
                      child: Column(
                        children: [
                          Text(
                            getLaneStatus(),
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              fontSize: 32,
                              fontWeight: FontWeight.bold,
                              color: getLaneColor(),
                              letterSpacing: 2,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            laneLight == 1
                                ? '⚠️ Emergency / High Traffic'
                                : '✅ Lane is Clear',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              fontSize: 16,
                              color: Colors.grey[400],
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),

                    // Binary Value Display
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.grey[900],
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        'Value: $laneLight',
                        style: const TextStyle(
                          fontSize: 16,
                          fontFamily: 'monospace',
                          color: Colors.greenAccent,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),

            // Quick Reference Card
            Card(
              color: Colors.blue.withOpacity(0.1),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: const [
                        Icon(Icons.info_outline, color: Colors.blue),
                        SizedBox(width: 8),
                        Text(
                          'Quick Reference',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    _buildReferenceRow('🔴 RED', '100', Colors.red),
                    const SizedBox(height: 8),
                    _buildReferenceRow('🟡 YELLOW', '010', Colors.yellow),
                    const SizedBox(height: 8),
                    _buildReferenceRow('🟢 GREEN', '001', Colors.green),
                    const Divider(height: 24),
                    _buildReferenceRow('🚨 Congested', '1', Colors.red),
                    const SizedBox(height: 8),
                    _buildReferenceRow('✅ Free', '0', Colors.green),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTrafficBulb(Color color, bool isActive) {
    return AnimatedBuilder(
      animation: _pulseController,
      builder: (context, child) {
        return Container(
          width: 70,
          height: 70,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: isActive ? color : Colors.grey[800],
            boxShadow: isActive
                ? [
              BoxShadow(
                color: color.withOpacity(0.6 + (_pulseController.value * 0.4)),
                blurRadius: 30,
                spreadRadius: 10,
              ),
            ]
                : null,
          ),
        );
      },
    );
  }

  Widget _buildReferenceRow(String label, String code, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          Container(
            width: 12,
            height: 12,
            decoration: BoxDecoration(
              color: color,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              label,
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
            decoration: BoxDecoration(
              color: Colors.grey[900],
              borderRadius: BorderRadius.circular(6),
            ),
            child: Text(
              code,
              style: const TextStyle(
                fontSize: 14,
                fontFamily: 'monospace',
                color: Colors.greenAccent,
              ),
            ),
          ),
        ],
      ),
    );
  }
}