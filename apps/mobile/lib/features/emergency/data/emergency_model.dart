class EmergencyContact {
  final int id;
  final String name;
  final String phoneNumber;
  final int? categoryId;
  final String description;
  final String availability;

  const EmergencyContact({
    required this.id,
    required this.name,
    required this.phoneNumber,
    this.categoryId,
    required this.description,
    required this.availability,
  });

  factory EmergencyContact.fromJson(
    Map<String, dynamic> json,
  ) {
    return EmergencyContact(
      id: json['contact_id'] as int,
      name: json['name'] as String,
      phoneNumber: json['phone_number'] as String,
      categoryId: json['category_id'] as int?,
      description: json['description'] as String,
      availability: json['availability'] as String,
    );
  }
}