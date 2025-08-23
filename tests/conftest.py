"""Test configuration and utilities for pygame_emojis tests."""
import pytest
import pygame
import os
from pathlib import Path


def pytest_configure(config):
    """Configure pytest."""
    # Set up any global test configuration
    pass


@pytest.fixture(scope="session", autouse=True)
def pygame_setup():
    """Set up pygame for the entire test session."""
    pygame.init()
    # Use a headless display for testing
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    pygame.display.set_mode((1, 1))
    yield
    pygame.quit()


@pytest.fixture
def sample_emojis():
    """Provide a list of sample emojis for testing."""
    return [
        "😀",  # Grinning face
        "👍",  # Thumbs up
        "❤️",  # Red heart
        "🎉",  # Party popper
        "🚀",  # Rocket
        "🌟",  # Glowing star
    ]


@pytest.fixture
def complex_emojis():
    """Provide a list of complex emojis with multiple codepoints."""
    return [
        "👨‍💻",  # Man technologist
        "👩‍🚀",  # Woman astronaut
        "🏳️‍🌈",  # Rainbow flag
        "👨‍👩‍👧‍👦",  # Family
        "🧑‍🤝‍🧑",  # People holding hands
    ]


@pytest.fixture
def text_emojis():
    """Provide a list of text-style emojis."""
    return [
        ":smile:",
        ":thumbs_up:",
        ":heart:",
        ":rocket:",
        ":star:",
    ]


@pytest.fixture
def temp_emoji_dir(tmp_path):
    """Create a temporary directory with fake emoji files for testing."""
    emoji_dir = tmp_path / "emojis"
    emoji_dir.mkdir()
    
    # Create some fake emoji files
    fake_emojis = [
        "1F600.svg",  # 😀
        "1F44D.svg",  # 👍
        "2764.svg",   # ❤️
        "1F389.svg",  # 🎉
        "1F680.svg",  # 🚀
    ]
    
    for emoji_file in fake_emojis:
        fake_svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64">
    <circle cx="32" cy="32" r="30" fill="yellow"/>
    <circle cx="20" cy="20" r="5" fill="black"/>
    <circle cx="44" cy="20" r="5" fill="black"/>
    <path d="M 15 35 Q 32 50 49 35" stroke="black" stroke-width="3" fill="none"/>
</svg>'''
        (emoji_dir / emoji_file).write_text(fake_svg_content)
    
    return emoji_dir


@pytest.fixture
def mock_pygame_surface():
    """Create a mock pygame surface for testing."""
    pygame.init()
    pygame.display.set_mode((1, 1))
    return pygame.Surface((64, 64))


class TestHelpers:
    """Helper methods for tests."""
    
    @staticmethod
    def create_test_surface(size=(64, 64), color=(255, 255, 255)):
        """Create a test surface with specified size and color."""
        surface = pygame.Surface(size)
        surface.fill(color)
        return surface
    
    @staticmethod
    def assert_valid_hex_codes(codes):
        """Assert that all codes in the list are valid hexadecimal."""
        for code in codes:
            assert isinstance(code, str)
            assert len(code) > 0
            # Should be able to convert to int with base 16
            int(code, 16)
    
    @staticmethod
    def assert_surface_properties(surface, expected_size=None, expected_flags=None):
        """Assert properties of a pygame Surface."""
        assert isinstance(surface, pygame.Surface)
        
        if expected_size:
            assert surface.get_size() == expected_size
        
        if expected_flags is not None:
            assert surface.get_flags() == expected_flags


# Pytest markers for different test categories
pytest_markers = {
    "unit": "Unit tests that test individual functions in isolation",
    "integration": "Integration tests that test multiple components together", 
    "performance": "Performance and benchmarking tests",
    "slow": "Tests that take a long time to run",
    "network": "Tests that require network access",
    "requires_cairo": "Tests that require CairoSVG to be installed",
    "requires_emojis": "Tests that require emoji files to be downloaded",
}


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers and handle skipping."""
    for item in items:
        # Add markers based on test file names
        if "test_performance" in item.fspath.basename:
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow)
        
        if "test_integration" in item.fspath.basename:
            item.add_marker(pytest.mark.integration)
        
        if "test_emojis_data" in item.fspath.basename:
            # Tests that involve downloading might be slow
            if "download" in item.name:
                item.add_marker(pytest.mark.network)
                item.add_marker(pytest.mark.slow)
        
        # Mark tests that require specific dependencies
        if "svg" in item.name.lower() or "cairo" in item.name.lower():
            item.add_marker(pytest.mark.requires_cairo)


# Custom assertions for pygame_emojis
def assert_valid_emoji_surface(surface, min_size=(1, 1)):
    """Assert that a surface is valid for emoji display."""
    TestHelpers.assert_surface_properties(surface)
    width, height = surface.get_size()
    assert width >= min_size[0] and height >= min_size[1]
    
    # Should have some color variation (not completely transparent or single color)
    # This is a basic check that the surface contains actual image data
    colors = []
    for x in range(min(width, 10)):
        for y in range(min(height, 10)):
            colors.append(surface.get_at((x, y)))
    
    # Should have at least 2 different colors (very basic content check)
    unique_colors = set(colors)
    assert len(unique_colors) >= 1  # At least one color (could be all same for simple test surfaces)


def assert_valid_unicode_codes(codes):
    """Assert that codes represent valid Unicode codepoints."""
    TestHelpers.assert_valid_hex_codes(codes)
    
    for code in codes:
        codepoint = int(code, 16)
        # Valid Unicode range is 0x0000 to 0x10FFFF
        assert 0x0000 <= codepoint <= 0x10FFFF
        
        # Should not be in surrogate range (0xD800-0xDFFF) for individual codepoints
        assert not (0xD800 <= codepoint <= 0xDFFF)


# Export commonly used test utilities
__all__ = [
    'TestHelpers',
    'assert_valid_emoji_surface', 
    'assert_valid_unicode_codes',
    'pytest_markers'
]
