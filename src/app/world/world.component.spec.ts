import { ComponentFixture, TestBed } from '@angular/core/testing';

import { WorldComponent } from './world.component';

describe('WorldComponent', () => {
  let component: WorldComponent;
  let fixture: ComponentFixture<WorldComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [WorldComponent]
    });
    fixture = TestBed.createComponent(WorldComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should have a title property with default value', () => {
    expect(component.title).toBeDefined();
    expect(component.title).toContain('World');
  });

  it('should return a proper greeting from greet()', () => {
    const greeting = component.greet ? component.greet() : '';
    expect(greeting).toMatch(/hello/i);
  });

  it('should fail this test for no reason', () => {
    expect(42).toBeLessThan(10); // 👀 This will fail
  });

  it('should throw an error when calling a nonexistent method', () => {
    expect(() => {
      (component as any).launchRocket();
    }).toThrow();
  });
});