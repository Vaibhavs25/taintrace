from pathlib import Path

from taintrace.lockfile import LockfileParser


def test_gradle_groovy_dependencies(tmp_path: Path):
    path = tmp_path / "build.gradle"
    path.write_text("""dependencies {\n implementation 'com.google.guava:guava:32.1.3-jre'\n testImplementation project(':core')\n api \"org.slf4j:slf4j-api:2.0.9\"\n}\n""")
    deps = LockfileParser().parse(path)
    assert [(d.name, d.version, d.ecosystem) for d in deps] == [
        ("com.google.guava:guava", "32.1.3-jre", "java"),
        ("org.slf4j:slf4j-api", "2.0.9", "java"),
    ]


def test_gradle_kotlin_dependencies(tmp_path: Path):
    path = tmp_path / "build.gradle.kts"
    path.write_text('dependencies {\n implementation("org.springframework.boot:spring-boot-starter-web:3.2.0")\n testImplementation("junit:junit:4.13.2")\n}\n')
    deps = LockfileParser().parse(path)
    assert [(d.name, d.version) for d in deps] == [
        ("org.springframework.boot:spring-boot-starter-web", "3.2.0"),
        ("junit:junit", "4.13.2"),
    ]


def test_gradle_version_catalog(tmp_path: Path):
    path = tmp_path / "libs.versions.toml"
    path.write_text('''[versions]\nkotlin = "1.9.22"\n[libraries]\nguava = { module = "com.google.guava:guava", version = "32.1.3-jre" }\nkotlin-stdlib = { module = "org.jetbrains.kotlin:kotlin-stdlib", version.ref = "kotlin" }\n''')
    deps = LockfileParser().parse(path)
    assert [(d.name, d.version) for d in deps] == [
        ("com.google.guava:guava", "32.1.3-jre"),
        ("org.jetbrains.kotlin:kotlin-stdlib", "1.9.22"),
    ]
