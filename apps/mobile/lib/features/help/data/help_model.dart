class HelpFacility {
  final int id;
  final String name;
  final String type;
  final String address;
  final double latitude;
  final double longitude;
  final String? phone;
  final String? email;
  final String? openingHours;
  final int capacity;
  final int? categoryId;

  const HelpFacility({
    required this.id,
    required this.name,
    required this.type,
    required this.address,
    required this.latitude,
    required this.longitude,
    required this.phone,
    required this.email,
    required this.openingHours,
    required this.capacity,
    required this.categoryId,
  });

  factory HelpFacility.fromJson(
    Map<String, dynamic> json,
  ) {
    return HelpFacility(
      id: json['facility_id'] as int,
      name: json['name'] as String,
      type: json['facility_type'] as String,
      address: json['address'] as String,
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      phone: json['phone'] as String?,
      email: json['email'] as String?,
      openingHours: json['opening_hours'] as String?,
      capacity: json['capacity'] as int,
      categoryId: json['category_id'] as int?,
    );
  }
}