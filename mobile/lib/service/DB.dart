import 'package:path/path.dart';
import 'package:sqflite/sqflite.dart';

class DB {
  static const String _databaseName = "mydb.db";
  static const int _databaseVersion = 1;

  static const String _table = "storage";

  static const String columnKey = "key";
  static const String columnValue = "value";

  static const String keyJWT = "jwt";
  static const String keyUser = "user";
  static const String keyFCM = "fcm";

  DB._();

  static final DB instance = DB._();

  Database? _database;

  Future<Database> get database async {
    _database ??= await _initDatabase();
    return _database!;
  }

  Future<Database> _initDatabase() async {
    final databasesPath = await getDatabasesPath();
    final path = join(databasesPath, _databaseName);

    return openDatabase(path, version: _databaseVersion, onCreate: _onCreate);
  }

  Future<void> _onCreate(Database db, int version) async {
    await db.execute("""
      CREATE TABLE $_table (
        $columnKey TEXT PRIMARY KEY,
        $columnValue TEXT NOT NULL
      )
    """);
  }

  Future<void> _save(String key, String value) async {
    final db = await database;

    await db.insert(_table, {
      columnKey: key,
      columnValue: value,
    }, conflictAlgorithm: ConflictAlgorithm.replace);
  }

  Future<String?> _get(String key) async {
    final db = await database;

    final result = await db.query(
      _table,
      where: "$columnKey = ?",
      whereArgs: [key],
      limit: 1,
    );

    if (result.isEmpty) {
      return null;
    }

    return result.first[columnValue] as String;
  }

  Future<void> _delete(String key) async {
    final db = await database;

    await db.delete(_table, where: "$columnKey = ?", whereArgs: [key]);
  }

  Future<void> saveJWT(String jwt) async {
    await _save(keyJWT, jwt);
  }

  Future<String?> getJWT() async {
    return _get(keyJWT);
  }

  Future<void> deleteJWT() async {
    await _delete(keyJWT);
  }

  Future<void> saveUser(String user) async {
    await _save(keyUser, user);
  }

  Future<String?> getUser() async {
    return _get(keyUser);
  }

  Future<void> deleteUser() async {
    await _delete(keyUser);
  }

  Future<void> saveFCM(String token) async {
    await _save(keyFCM, token);
  }

  Future<String?> getFCM() async {
    return _get(keyFCM);
  }

  Future<void> deleteFCM() async {
    await _delete(keyFCM);
  }

  Future<void> clear() async {
    final db = await database;
    await db.delete(_table);
  }

  Future<void> close() async {
    if (_database != null) {
      await _database!.close();
      _database = null;
    }
  }
}

/*
  Salvar JWT:
  await DB.instance.saveJWT(jwt);

  Ler JWT:
  final jwt = await DB.instance.getJWT();

  Remover JWT:
  await DB.instance.deleteJWT();

  Salvar usuário (JSON):
  await DB.instance.saveUser(userJson);

  Ler usuário:
  final user = await DB.instance.getUser();

  Remover usuário:
  await DB.instance.deleteUser();

  Salvar FCM:
  await DB.instance.saveFCM(fcmToken);

  Ler FCM:
  final fcm = await DB.instance.getFCM();

  Remover FCM:
  await DB.instance.deleteFCM();

  Logout:
  await DB.instance.clear();
*/
