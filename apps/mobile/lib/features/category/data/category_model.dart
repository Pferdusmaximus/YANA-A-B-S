
class YanaCategory {
  final int id;
  final String name;
  final String? description;

  const YanaCategory({
    required this.id,
    required this.name,
    this.description,
  });

  factory YanaCategory.fromJson(
    Map<String, dynamic> json,
  ) {
    return YanaCategory(
      id: json['category_id'] as int,
      name: json['name'] as String,
      description: json['description'] as String?,
    );
  }
}
