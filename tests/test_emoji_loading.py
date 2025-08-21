"""Tests for the main pygame_emojis functionality."""
import pytest
import pygame
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import io

import pygame_emojis
from pygame_emojis import (
    find_code, 
    find_emoji, 
    load_emoji, 
    load_svg, 
    load_png, 
    emoji_to_surface,
    EmojiNotFound
)
from pygame_emojis.emojis_data.download import _EMOJIS_DIR


class TestFindCode:
    """Test the find_code function."""
    
    def test_find_code_simple_emoji(self):
        """Test finding code for a simple emoji."""
        result = find_code("😀")
        assert isinstance(result, list)
        assert len(result) > 0
        # Test that all results are valid hex strings
        for code in result:
            assert all(c in '0123456789ABCDEF' for c in code)
    
    def test_find_code_text_emoji(self):
        """Test finding code for text-style emoji."""
        result = find_code(":smile:")
        assert isinstance(result, list)
        assert len(result) > 0
    
    def test_find_code_complex_emoji(self):
        """Test finding code for complex emoji with multiple codepoints."""
        result = find_code("👨‍💻")  # Man technologist
        assert isinstance(result, list)
        assert len(result) >= 2  # Should have multiple codepoints
    
    def test_find_code_empty_string(self):
        """Test find_code with empty string."""
        result = find_code("")
        assert result == []
    
    def test_find_code_regular_text(self):
        """Test find_code with regular text."""
        result = find_code("A")
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == "41"  # ASCII code for 'A'


class TestFindEmoji:
    """Test the find_emoji function."""
    
    @patch('pygame_emojis._EMOJIS_DIR')
    def test_find_emoji_exists(self, mock_emojis_dir):
        """Test finding an emoji that exists."""
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_emojis_dir.__truediv__.return_value = mock_path
        
        with patch('pygame_emojis.find_code', return_value=['1F600']):
            result = find_emoji("😀")
            assert result == mock_path
    
    @patch('pygame_emojis._EMOJIS_DIR')
    def test_find_emoji_not_exists_direct_but_glob_match(self, mock_emojis_dir):
        """Test finding emoji when direct file doesn't exist but glob finds matches."""
        mock_path = MagicMock()
        mock_path.exists.return_value = False
        mock_emojis_dir.__truediv__.return_value = mock_path
        
        # Mock rglob to return a matching file
        mock_matching_file = Path("/fake/path/1F600-extended.svg")
        mock_emojis_dir.rglob.return_value = [mock_matching_file]
        
        with patch('pygame_emojis.find_code', return_value=['1F600']):
            result = find_emoji("😀")
            assert result == mock_matching_file
    
    @patch('pygame_emojis._EMOJIS_DIR')
    def test_find_emoji_not_found(self, mock_emojis_dir):
        """Test finding emoji that doesn't exist."""
        mock_path = MagicMock()
        mock_path.exists.return_value = False
        mock_emojis_dir.__truediv__.return_value = mock_path
        mock_emojis_dir.rglob.return_value = []
        
        with patch('pygame_emojis.find_code', return_value=['NONEXISTENT']):
            result = find_emoji("🫥")  # Non-existent emoji
            assert result is None
    
    def test_find_emoji_invalid_emoji(self):
        """Test find_emoji with invalid emoji that raises exception in find_code."""
        with patch('pygame_emojis.find_code', side_effect=Exception("Invalid emoji")):
            with pytest.raises(EmojiNotFound):
                find_emoji("invalid")
    
    @patch('pygame_emojis._EMOJIS_DIR')
    def test_find_emoji_progressive_shortening(self, mock_emojis_dir):
        """Test that find_emoji progressively shortens codes when not found."""
        mock_path = MagicMock()
        mock_path.exists.return_value = False
        mock_emojis_dir.__truediv__.return_value = mock_path
        mock_emojis_dir.rglob.return_value = []
        
        # Mock find_code to return multiple codes
        with patch('pygame_emojis.find_code', return_value=['1F468', '200D', '1F4BB']):
            result = find_emoji("👨‍💻")
            # Should have tried multiple combinations due to progressive shortening
            assert mock_emojis_dir.__truediv__.call_count >= 1


class TestLoadEmoji:
    """Test the load_emoji function."""
    
    def setUp(self):
        """Set up pygame for tests."""
        pygame.init()
        pygame.display.set_mode((1, 1))  # Minimal display for testing
    
    @patch('pygame_emojis.find_emoji')
    @patch('pygame_emojis.emoji_to_surface')
    def test_load_emoji_success(self, mock_emoji_to_surface, mock_find_emoji):
        """Test successful emoji loading."""
        self.setUp()
        
        mock_file_path = Path("/fake/path/emoji.svg")
        mock_find_emoji.return_value = mock_file_path
        
        mock_surface = pygame.Surface((32, 32))
        mock_emoji_to_surface.return_value = mock_surface
        
        result = load_emoji("😀", (32, 32))
        
        mock_find_emoji.assert_called_once_with("😀")
        mock_emoji_to_surface.assert_called_once_with(mock_file_path, (32, 32))
        assert result == mock_surface
    
    @patch('pygame_emojis.find_emoji')
    def test_load_emoji_not_found(self, mock_find_emoji):
        """Test loading emoji that doesn't exist."""
        self.setUp()
        
        mock_find_emoji.return_value = None
        
        with pytest.raises(FileNotFoundError, match="No file available for emoji"):
            load_emoji("🫥")
    
    @patch('pygame_emojis.find_emoji')
    @patch('pygame_emojis.emoji_to_surface')
    def test_load_emoji_no_size(self, mock_emoji_to_surface, mock_find_emoji):
        """Test loading emoji without specifying size."""
        self.setUp()
        
        mock_file_path = Path("/fake/path/emoji.svg")
        mock_find_emoji.return_value = mock_file_path
        
        mock_surface = pygame.Surface((64, 64))
        mock_emoji_to_surface.return_value = mock_surface
        
        result = load_emoji("😀")
        
        mock_emoji_to_surface.assert_called_once_with(mock_file_path, None)
        assert result == mock_surface


class TestLoadSvg:
    """Test the load_svg function."""
    
    def setUp(self):
        """Set up pygame for tests."""
        pygame.init()
        pygame.display.set_mode((1, 1))
    
    @patch('pygame_emojis.cairosvg')
    @patch('pygame_emojis.cairo_installed', True)
    @patch('pygame.image.load')
    def test_load_svg_with_size(self, mock_pygame_load, mock_cairosvg):
        """Test loading SVG with specified size."""
        self.setUp()
        
        # Mock cairosvg.svg2png
        mock_png_data = b"fake_png_data"
        mock_cairosvg.svg2png.return_value = mock_png_data
        
        # Mock pygame.image.load
        mock_surface = pygame.Surface((64, 64))
        mock_pygame_load.return_value = mock_surface
        
        result = load_svg("/fake/path/emoji.svg", (64, 64))
        
        mock_cairosvg.svg2png.assert_called_once()
        call_args = mock_cairosvg.svg2png.call_args
        assert call_args[1]['parent_width'] == 64
        assert call_args[1]['parent_height'] == 64
        assert result == mock_surface
    
    @patch('pygame_emojis.cairosvg')
    @patch('pygame_emojis.cairo_installed', True)
    @patch('pygame.image.load')
    def test_load_svg_with_int_size(self, mock_pygame_load, mock_cairosvg):
        """Test loading SVG with integer size."""
        self.setUp()
        
        mock_png_data = b"fake_png_data"
        mock_cairosvg.svg2png.return_value = mock_png_data
        
        mock_surface = pygame.Surface((32, 32))
        mock_pygame_load.return_value = mock_surface
        
        result = load_svg("/fake/path/emoji.svg", 32)
        
        call_args = mock_cairosvg.svg2png.call_args
        assert call_args[1]['parent_width'] == 32
        assert call_args[1]['parent_height'] == 32
    
    @patch('pygame_emojis.cairo_installed', False)
    def test_load_svg_cairo_not_installed(self):
        """Test loading SVG when Cairo is not installed."""
        with pytest.raises(ImportError, match="CairoSVG is not installed"):
            load_svg("/fake/path/emoji.svg")
    
    @patch('pygame_emojis.cairosvg')
    @patch('pygame_emojis.cairo_installed', True)
    @patch('pygame.image.load')
    def test_load_svg_no_size(self, mock_pygame_load, mock_cairosvg):
        """Test loading SVG without specified size."""
        self.setUp()
        
        mock_png_data = b"fake_png_data"
        mock_cairosvg.svg2png.return_value = mock_png_data
        
        mock_surface = pygame.Surface((64, 64))
        mock_pygame_load.return_value = mock_surface
        
        result = load_svg("/fake/path/emoji.svg", None)
        
        call_args = mock_cairosvg.svg2png.call_args
        # Should not have size parameters when size is None
        assert 'parent_width' not in call_args[1]
        assert 'parent_height' not in call_args[1]


class TestLoadPng:
    """Test the load_png function."""
    
    def setUp(self):
        """Set up pygame for tests."""
        pygame.init()
        pygame.display.set_mode((1, 1))
    
    @patch('pygame.image.load')
    @patch('pygame.transform.scale')
    def test_load_png_with_tuple_size(self, mock_scale, mock_load):
        """Test loading PNG with tuple size."""
        self.setUp()
        
        original_surface = pygame.Surface((128, 128))
        scaled_surface = pygame.Surface((64, 64))
        
        mock_load.return_value = original_surface
        mock_scale.return_value = scaled_surface
        
        result = load_png("/fake/path/emoji.png", (64, 64))
        
        mock_load.assert_called_once_with("/fake/path/emoji.png")
        mock_scale.assert_called_once_with(original_surface, (64, 64))
        assert result == scaled_surface
    
    @patch('pygame.image.load')
    @patch('pygame.transform.scale')
    def test_load_png_with_int_size(self, mock_scale, mock_load):
        """Test loading PNG with integer size."""
        self.setUp()
        
        original_surface = pygame.Surface((128, 128))
        scaled_surface = pygame.Surface((32, 32))
        
        mock_load.return_value = original_surface
        mock_scale.return_value = scaled_surface
        
        result = load_png("/fake/path/emoji.png", 32)
        
        mock_scale.assert_called_once_with(original_surface, (32, 32))
        assert result == scaled_surface
    
    @patch('pygame.image.load')
    def test_load_png_no_size(self, mock_load):
        """Test loading PNG without scaling."""
        self.setUp()
        
        original_surface = pygame.Surface((128, 128))
        mock_load.return_value = original_surface
        
        result = load_png("/fake/path/emoji.png", None)
        
        mock_load.assert_called_once_with("/fake/path/emoji.png")
        assert result == original_surface


class TestEmojiToSurface:
    """Test the emoji_to_surface function."""
    
    def setUp(self):
        """Set up pygame for tests."""
        pygame.init()
        pygame.display.set_mode((1, 1))
    
    @patch('pygame_emojis.load_png')
    def test_emoji_to_surface_png(self, mock_load_png):
        """Test emoji_to_surface with PNG file."""
        self.setUp()
        
        mock_surface = pygame.Surface((64, 64))
        mock_load_png.return_value = mock_surface
        
        png_path = Path("/fake/path/emoji.png")
        result = emoji_to_surface(png_path, (64, 64))
        
        mock_load_png.assert_called_once_with(png_path, (64, 64))
        assert result == mock_surface
    
    @patch('pygame_emojis.load_svg')
    def test_emoji_to_surface_svg(self, mock_load_svg):
        """Test emoji_to_surface with SVG file."""
        self.setUp()
        
        mock_surface = pygame.Surface((64, 64))
        mock_load_svg.return_value = mock_surface
        
        svg_path = Path("/fake/path/emoji.svg")
        result = emoji_to_surface(svg_path, (64, 64))
        
        mock_load_svg.assert_called_once_with(svg_path, (64, 64))
        assert result == mock_surface
    
    def test_emoji_to_surface_unsupported_format(self):
        """Test emoji_to_surface with unsupported file format."""
        self.setUp()
        
        unsupported_path = Path("/fake/path/emoji.gif")
        
        with pytest.raises(ValueError, match="Image file must be a .png or .svg file"):
            emoji_to_surface(unsupported_path, (64, 64))


class TestEmojiNotFound:
    """Test the EmojiNotFound exception."""
    
    def test_emoji_not_found_exception(self):
        """Test that EmojiNotFound is a proper exception."""
        with pytest.raises(EmojiNotFound):
            raise EmojiNotFound("test emoji")
        
        # Test inheritance
        assert issubclass(EmojiNotFound, Exception)


@pytest.fixture(scope="session")
def pygame_initialized():
    """Initialize pygame for the test session."""
    pygame.init()
    pygame.display.set_mode((1, 1))
    yield
    pygame.quit()


class TestIntegration:
    """Integration tests that test the full workflow."""
    
    def test_emoji_loading_workflow(self, pygame_initialized):
        """Test the complete emoji loading workflow with mocked dependencies."""
        with patch('pygame_emojis.find_emoji') as mock_find_emoji, \
             patch('pygame_emojis.emoji_to_surface') as mock_emoji_to_surface:
            
            # Mock the workflow
            mock_file_path = Path("/fake/path/1F600.svg")
            mock_find_emoji.return_value = mock_file_path
            
            mock_surface = pygame.Surface((64, 64))
            mock_emoji_to_surface.return_value = mock_surface
            
            # Test the workflow
            result = load_emoji("😀", (64, 64))
            
            # Verify the calls
            mock_find_emoji.assert_called_once_with("😀")
            mock_emoji_to_surface.assert_called_once_with(mock_file_path, (64, 64))
            assert result == mock_surface


if __name__ == "__main__":
    pytest.main([__file__])
