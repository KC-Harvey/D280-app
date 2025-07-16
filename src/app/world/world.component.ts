import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-world',
  templateUrl: './world.component.html',
  styleUrls: ['./world.component.css']
})
export class WorldComponent implements OnInit {
  ngOnInit(): void {
    let svgPaths = document.querySelectorAll<SVGPathElement>('path');
    svgPaths.forEach(svgCountry => {
      svgCountry.addEventListener('click', () => {
        this.loadCountryData(svgCountry);
      });
    });
  }

  async loadCountryData(svgCountry: SVGPathElement) {
    const apiURL = `https://api.worldbank.org/V2/country/${svgCountry.id}?format=json`;

    try {
      const response = await fetch(apiURL);
      if (response.ok) {
        const data = await response.json();
        const countryData = data[1][0];

        document.getElementById('countrySpan')!.innerText = countryData.name;
        document.getElementById('capitalSpan')!.innerText = countryData.capitalCity;
        document.getElementById('regionSpan')!.innerText = countryData.region.value;
        document.getElementById('incomeSpan')!.innerText = countryData.incomeLevel.value;
        document.getElementById('latitudeSpan')!.innerText = countryData.latitude;
        document.getElementById('longitudeSpan')!.innerText = countryData.longitude;
      } else {
        console.error('Failed to fetch country data');
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }
}