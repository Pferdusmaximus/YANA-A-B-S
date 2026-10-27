class Category {
  final int id;
  final String name;
  final String? description;

  const Category({
    required this.id,
    required this.name,
    this.description,
  });

  factory Category.fromJson(Map<String, dynamic> json) {
    return Category(
      id: json['category_id'] as int,
      name: json['name'] as String,
      description: json['description'] as String?,
    );
  }
}
