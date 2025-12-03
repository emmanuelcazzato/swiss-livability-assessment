# Swiss Livability Assessment - Web Application Guide

## 🌐 Quick Start Guide

### **Prerequisites**

Make sure you have Python 3.9+ installed with the required packages:

```bash
pip install flask pandas numpy scikit-fuzzy matplotlib seaborn scipy networkx
```

Or use the requirements.txt:

```bash
pip install -r requirements.txt
```

---

## 🚀 Running the Web Application

### **Step 1: Navigate to Project Folder**

Open Terminal (Mac/Linux) or Command Prompt (Windows) and navigate to the project:

```bash
cd path/to/swiss_livability
```

### **Step 2: Start the Web Server**

Run the Flask application:

```bash
python web_app.py
```

Or on Mac/Linux:

```bash
python3 web_app.py
```

### **Step 3: Open in Browser**

Once the server starts, you'll see:

```
================================================================================
SWISS RESIDENTIAL PERCEIVED LIVABILITY ASSESSMENT
Web Interface - Proof of Concept
================================================================================

Starting web server...
Open your browser and go to: http://localhost:5000

Press Ctrl+C to stop the server
================================================================================
```

**Open your web browser** and go to:

```
http://localhost:5000
```

---

## 📱 Features

### **1. Home Page**
- Overview of the fuzzy livability assessment system
- Explanation of the four dimensions assessed
- Information about livability levels (Excellent/Good/Fair/Poor)

### **2. Explore Data**
- View summary statistics from the Swiss Dwellings dataset
- Browse sample dwellings with their environmental parameters
- Quick assess button for each dwelling

### **3. Assess Dwelling**
- Interactive form to input environmental parameters:
  - **Noise levels** (Lden and Lnight in dB)
  - **Daylight illuminance** (in lux)
  - **View quality** (sky and greenery in steradians)
  - **Location convenience** (POI count)
- Real-time FLI computation
- Detailed breakdown by dimension
- Personalized recommendations

---

## 🎨 Web Interface Design

The web interface features:

- **Modern, clean design** with gradient backgrounds
- **Responsive layout** that works on desktop and mobile
- **Interactive forms** with real-time validation
- **Visual feedback** with color-coded scores
- **Easy navigation** between pages
- **Professional styling** inspired by modern web apps

---

## 🔧 Troubleshooting

### **Issue: "Module not found" errors**

**Solution:** Install missing packages:

```bash
pip install flask pandas numpy scikit-fuzzy scipy networkx
```

### **Issue: "Address already in use"**

**Solution:** Another application is using port 5000. Either:
1. Stop the other application
2. Or modify `web_app.py` line 204 to use a different port:

```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change 5000 to 5001
```

### **Issue: "Data not loaded"**

**Solution:** Make sure the file paths are correct. The app looks for:

```
swiss_livability/data/processed/dwellings_sample.csv
```

If the file doesn't exist, run `create_sample_data.py` first:

```bash
python create_sample_data.py
```

### **Issue: Can't access from another device**

**Solution:** The app runs on `0.0.0.0` which means it's accessible from other devices on your network. Find your IP address:

**Mac/Linux:**
```bash
ifconfig | grep "inet "
```

**Windows:**
```bash
ipconfig
```

Then access from another device using:
```
http://YOUR_IP_ADDRESS:5000
```

---

## 📊 Using the Assessment Tool

### **Example 1: Excellent Dwelling**

```
Noise Lden: 45 dB (Quiet)
Noise Lnight: 35 dB (Quiet)
Daylight: 450 lux (High)
Sky View: 1.0 sr (Good)
Greenery View: 0.8 sr (Good)
POI Count: 70 (Medium)

Expected FLI: ~80-85 (Excellent)
```

### **Example 2: Poor Dwelling**

```
Noise Lden: 70 dB (Noisy)
Noise Lnight: 60 dB (Noisy)
Daylight: 80 lux (Low)
Sky View: 0.2 sr (Limited)
Greenery View: 0.1 sr (Limited)
POI Count: 20 (Low)

Expected FLI: ~15-25 (Poor)
```

### **Example 3: Good Dwelling**

```
Noise Lden: 55 dB (Moderate)
Noise Lnight: 45 dB (Moderate)
Daylight: 300 lux (Medium)
Sky View: 0.6 sr (Moderate)
Greenery View: 0.4 sr (Moderate)
POI Count: 60 (Medium)

Expected FLI: ~50-60 (Good)
```

---

## 🎯 For Your Professor Meeting

### **What to Show:**

1. **Start the web app** before the meeting
2. **Open the Home page** - explain the concept
3. **Navigate to Explore Data** - show the dataset statistics
4. **Go to Assess Dwelling** - demonstrate live FLI computation
5. **Try different scenarios** - show how FLI changes with inputs

### **Key Points to Highlight:**

✅ **Real-time assessment** - instant FLI computation  
✅ **Standards-based** - WHO 2018 and EN 17037 thresholds  
✅ **Interpretable** - clear linguistic labels and recommendations  
✅ **Interactive** - users can experiment with different parameters  
✅ **Scalable** - can process entire dataset (45,176 dwellings)  

---

## 📝 Technical Details

### **Architecture:**

- **Backend:** Flask (Python web framework)
- **Frontend:** HTML5, CSS3, JavaScript
- **Fuzzy Logic:** scikit-fuzzy library
- **Data Processing:** pandas, numpy
- **API:** RESTful endpoints for assessment

### **File Structure:**

```
swiss_livability/
├── web_app.py                 # Main Flask application
├── templates/                 # HTML templates
│   ├── base.html             # Base template with navigation
│   ├── index.html            # Home page
│   ├── explore.html          # Data exploration page
│   └── assess.html           # Assessment page
├── static/                    # Static files (CSS, JS)
├── src/                       # Fuzzy logic modules
│   ├── fuzzy_system.py
│   ├── membership_functions.py
│   └── rule_base.py
└── data/                      # Dataset files
    └── processed/
        └── dwellings_sample.csv
```

---

## 🌟 Future Enhancements

Potential improvements for the full version:

1. **User Authentication** - Save assessments and comparisons
2. **Spatial Visualization** - Map view of FLI scores across Switzerland
3. **Comparison Tool** - Compare multiple dwellings side-by-side
4. **Historical Tracking** - Track livability changes over time
5. **Export Functionality** - Download reports as PDF
6. **Advanced Filtering** - Filter dwellings by canton, price, type
7. **Mobile App** - Native iOS/Android application
8. **API Access** - RESTful API for third-party integrations

---

## 📞 Support

For issues or questions about the web application, refer to:

- **README.md** - Project overview
- **FINAL_README.md** - Complete documentation
- **docs/literature_review.md** - Theoretical background

---

**Happy Assessing!** 🏠✨

